import os
import secrets
from json import JSONEncoder
from secrets import token_hex
from typing import List

from flask import Flask, render_template, flash, url_for, send_from_directory, request
from flask_cors import CORS
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from werkzeug.utils import secure_filename, redirect
from wtforms import StringField, FileField, SubmitField, TextAreaField
from wtforms.validators import InputRequired, DataRequired, Length

from application import db, migrate
from application.game_service import GameService, GameStats
from common.enums import CardType, DeckType
from core.card import Card
from core.hand import Hand
from core.player import Player

basedir: str = os.path.abspath(os.path.dirname(__file__))
db_dir: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) + "/database"
migration_dir: str = db_dir + "/migrations"

VERSION: str = "2.0"

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite+pysqlite:///{}/roborally.db".format(db_dir)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["jpeg", "jpg", "png", "gif"]
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["AVATAR_UPLOADS"] = os.path.join(basedir, "static/images/avatars")
app.config["BOARD_UPLOADS"] = os.path.join(basedir, "static/images/board_states")

# Uncomment for local
cors = CORS(app, origins=["http://localhost:5000", "http://127.0.0.1:5000"])

# Uncomment for ECs
#app.config['SERVER_NAME'] = "roborally"
#cors = CORS(app, origins=["http://roborally.mylio-internal.com"])

db.init_app(app)
migrate.init_app(app, db, directory=migration_dir)

# Comment when running alembic commands
game_service: GameService = GameService(app.config["BOARD_UPLOADS"])


class NewPlayerForm(FlaskForm):
    name = StringField("Name", validators=[InputRequired("Input is required!"), DataRequired("Data is required!"),
        Length(min=3, max=32, message="Input must be between 3 and 32 characters long")])
    avatar = FileField("Avatar",
                       validators=[FileRequired(), FileAllowed(app.config["ALLOWED_IMAGE_EXTENSIONS"], "Images only!")])
    submit = SubmitField("Submit")


class NewGameForm(FlaskForm):
    cancel = SubmitField("Cancel")
    doit = SubmitField("Do it")


class BoardStateForm(FlaskForm):
    save = SubmitField("Save Notes")
    notes = TextAreaField("Notes",
                          validators=[Length(max=1000, message="Input must be under 1000 characters")])
    add = FileField("Add image",
                    validators=[FileAllowed(app.config["ALLOWED_IMAGE_EXTENSIONS"], "Images only!")])
    submit = SubmitField("Submit")


class PlayTurnForm(FlaskForm):
    submit = SubmitField("Next Turn")


class DeletePlayerForm(FlaskForm):
    pass


class PublicCardForm(FlaskForm):
    pass


class PlayerDetailsForm(FlaskForm):
    submit = SubmitField("Lock your choices for the upcoming turn")
    save = SubmitField("Save Instructions")
    active = SubmitField("Abstain from game")
    power_down = SubmitField("Power down")
    power_up = SubmitField("Power up")
    draw_power_card = SubmitField("")
    inc_damage = SubmitField("+")
    dec_damage = SubmitField("-")
    instructions = TextAreaField("Instructions",
                                 validators=[Length(max=1000, message="Input must be under 1000 characters")])


@app.route("/")
def home_page():
    players: List[Player] = game_service.players
    stats: GameStats = game_service.get_game_stats()

    return render_template("home.html", players=players, stats=stats, version=VERSION)


@app.route("/cards/<type>")
def cards_page(type):
    cards: List[Card] = game_service.get_cards(type)
    stats: GameStats = game_service.get_game_stats()

    prefix: str = "images/"
    if type == CardType.POWER:
        prefix = "images/power_cards/"
    if type == CardType.PROGRAM:
        prefix = "images/program_cards/"

    return render_template("cards.html", cards=cards, prefix=prefix, stats=stats, version=VERSION, type=type)


@app.route("/public-cards", methods=["GET", "POST"])
def public_cards_page():
    for player in game_service.active_players:
        setattr(PublicCardForm, "draw_{}".format(player.id), SubmitField("Draw"))

        for card in player.power_hand.cards:
            setattr(PublicCardForm, "discard_{}_{}".format(player.id, card.number), SubmitField("Discard"))

    form: PublicCardForm = PublicCardForm()
    players: List[Player] = game_service.active_players
    stats: GameStats = game_service.get_game_stats()

    if form.validate_on_submit():
        if form.data:
            for name, value in form.data.items():
                if value:
                    parts = name.split('_')
                    action: str = parts[0]

                    if action == "draw":
                        id: str = parts[1]
                        player = _get_player(id)

                        try:
                            player.draw_power_card(game_service.game.power_deck)
                            game_service.save_game()

                            flash("Power card drawn for {}".format(player.name), "success")
                        except IndexError as err:
                            flash("Cannot draw any more power cards for {}".format(player.name), "warning")
                    else:
                        player_id: str = parts[1]
                        card_number: int = int(parts[2])
                        player = _get_player(player_id)

                        from_hand: Hand = player.get_hand_by_name(DeckType.POWER_HAND)
                        to_hand: Hand = game_service.discard_pile
                        from_hand.transfer_card_by_number(card_number, to_hand)
                        game_service.save_player(player)

                        flash("Power card discarded for {}".format(player.name), "success")

                    game_service.save_player(player)

                    break

            return redirect(url_for("public_cards_page"))

    return render_template("public_cards.html", form=form, players=players, stats=stats, version=VERSION)


@app.route("/new-game", methods=["GET", "POST"])
def new_game_page():
    form = NewGameForm()
    stats: GameStats = game_service.get_game_stats()

    if form.validate_on_submit():
        if form.doit.data:
            game_service.start_new_game(app.config["BOARD_UPLOADS"])

            flash("New game started", "success")

        return redirect(url_for("home_page"))

    return render_template("new_game.html", form=form, stats=stats, version=VERSION)


@app.route("/play-turn/<register>", methods=["GET", "POST"])
def play_turn_page(register):
    for player in game_service.players:
        setattr(PlayTurnForm, "inc_damage_{}".format(player.id), SubmitField("+"))
        setattr(PlayTurnForm, "dec_damage_{}".format(player.id), SubmitField("-"))

    form: PlayTurnForm = PlayTurnForm()
    stats: GameStats = game_service.get_game_stats()
    info = game_service.get_register_for_turn(int(register))

    if form.validate_on_submit():
        if form.submit.data:
            game_service.start_new_turn()

            flash("New turn started", "success")
            return redirect(url_for("home_page"))

        if form.data:
            for name, value in form.data.items():
                if value:
                    parts = name.split('_')
                    action: str = parts[0]
                    id: str = parts[2]
                    player = _get_player(id)

                    if player is not None:
                        if action == "inc":
                            player.inc_damage()
                            flash("Damage for {} increased by 1".format(player.name), "success")
                        else:
                            player.dec_damage()
                            flash("Damager for {} decreased by 1".format(player.name), "success")

                    game_service.save_player(player)

                    break

            return redirect(url_for("play_turn_page", register=register))

    return render_template("play_turn.html", form=form, stats=stats, version=VERSION, info=info, register=register)


def _get_player(id: str) -> Player:
    try:
        player: Player = game_service.get_player(id)
    except Exception as err:
        print("Problem finding player ID {}: {}".format(id, err))
        player = None

    return player


@app.route("/players/<player_id>", methods=["GET", "POST"])
def player_page(player_id):
    stats: GameStats = game_service.get_game_stats()
    player: Player = game_service.get_player(player_id)
    form = PlayerDetailsForm()

    if player.is_active:
        form.active.label.text = "Abstain from game"
    else:
        form.active.label.text = "Participate in game"

    if request.method == 'GET':
        form.instructions.data = player.instructions

    if form.validate_on_submit():
        if form.submit.data:
            if player.registers.any_empty:
                flash("You must fill all registers!", "warning")
            else:
                player.lock_choices()

        if form.active.data:
            player.is_active = not player.is_active

        if form.power_down.data:
            player.will_power_down()
            flash("Will power down next turn", "info")

        if form.power_up.data:
            player.will_power_up()
            flash("Will power up next turn", "info")

        if form.inc_damage.data:
            player.inc_damage()

        if form.dec_damage.data:
            player.dec_damage()

        if form.instructions.data:
            player.instructions = form.instructions.data
        else:
            player.instructions = ""

        game_service.save_player(player)
        return redirect(url_for("player_page", player_id=player.id))

    if player.is_destroyed:
        flash("Destroyed", "danger")

    if player.is_powered_down:
        flash("Currently powered down", "warning")

    return render_template("player.html", player=player, stats=stats, version=VERSION, form=form)


@app.route("/add", methods=["GET", "POST"])
def add_page():
    form = NewPlayerForm()
    stats: GameStats = game_service.get_game_stats()

    if form.validate_on_submit():
        random_string = token_hex(2)
        filename = random_string + "_" + form.avatar.data.filename
        filename = secure_filename(filename)
        form.avatar.data.save(os.path.join(app.config["AVATAR_UPLOADS"], filename))

        game_service.add_player(form.name.data, filename)

        flash("Player {} has been created".format(form.name.data), "success")
        return redirect(url_for("add_page"))

    if form.errors:
        flash("{}".format(form.errors), "danger")

    return render_template("add.html", form=form, stats=stats, version=VERSION)


@app.route("/delete", methods=["GET", "POST"])
def delete_page():
    stats: GameStats = game_service.get_game_stats()

    for player in game_service.players:
        setattr(DeletePlayerForm, player.id, SubmitField("Delete"))
    form: DeletePlayerForm = DeletePlayerForm()

    if form.validate_on_submit():
        if form.data:
            id = ""
            for name, value in form.data.items():
                if value:
                    id = name

                    break

            try:
                player: Player = game_service.delete_player(id, app.config['AVATAR_UPLOADS'])
            except Exception as err:
                print("Problem deleting player ID {}: {}".format(id, err))
                player = None

            if player is None:
                flash("Problem deleting player ID {}".format(id), "danger")
            else:
                try:
                    os.remove(os.path.join(app.config["AVATAR_UPLOADS"], player.avatar_filename))
                except Exception:
                    pass
                flash("Player {} has been deleted".format(player.name), "success")

        return redirect(url_for("delete_page"))

    players: List[Player] = game_service.players

    return render_template("delete.html", players=players, stats=stats, version=VERSION, form=form)


@app.route("/board-state", methods=["GET", "POST"])
def board_state_page():
    form = BoardStateForm()
    stats: GameStats = game_service.get_game_stats()
    state: game_service.BoardState = game_service.get_board_state()

    if request.method == 'GET':
        form.notes.data = state.notes

    if form.validate_on_submit():
        if form.submit.data:
            random_string = token_hex(2)
            filename = "{}_{}".format(random_string, form.add.data.filename)
            filename = secure_filename(filename)

            if not os.path.exists(app.config["BOARD_UPLOADS"]):
                os.mkdir(app.config["BOARD_UPLOADS"])
            form.add.data.save(os.path.join(app.config["BOARD_UPLOADS"], filename))

            game_service.add_board_state(filename)
            flash("Board image has been added", "success")

        if form.save.data:
            if form.notes.data:
                game_service.add_game_notes(form.notes.data)
            else:
                game_service.add_game_notes("")

            game_service.save_game()
            flash("Notes saved", "success")

        return redirect(url_for("board_state_page"))

    if form.errors:
        flash("{}".format(form.errors), "danger")

    return render_template("view_board.html", form=form, stats=stats, version=VERSION, state=state)


@app.route("/avatar/<filename>")
def avatar(filename):
    return send_from_directory(app.config["AVATAR_UPLOADS"], filename)


@app.route("/board/<filename>")
def board_state(filename):
    return send_from_directory(app.config["BOARD_UPLOADS"], filename)


# --------------------

class CustomJsonEncoder(JSONEncoder):
    def default(self, o):
        try:
            return o.__dict__
        except AttributeError:
            return {}


@app.route("/api/players")
def api_all_players():
    try:
        players: list[Player] = game_service.players
    except Exception as err:
        print("Problem getting all players: {}".format(err))
        players = []

    data: str = CustomJsonEncoder().encode(players).replace('"_', '"')
    return data


@app.route("/api/players/<player_id>")
def api_player(player_id):
    try:
        player: Player = game_service.get_player(player_id)
    except Exception as err:
        print("Problem finding player ID {}: {}".format(player_id, err))
        player = ""

    data: str = CustomJsonEncoder().encode(player).replace('"_', '"')
    return data


@app.route("/api/players/<player_id>/drawPowerCard")
def api_draw_power_card(player_id):
    try:
        player = game_service.get_player(player_id)
    except Exception as err:
        print("Problem finding player ID {}: {}".format(player_id, err))
        return ""

    try:
        player.draw_power_card(game_service.game.power_deck)
        game_service.save_game()
        game_service.save_player(player)
    except Exception as err:
        print("Problem drawing power card for player ID {}: {}".format(player_id, err))

    data: str = CustomJsonEncoder().encode(player).replace('"_', '"')
    return data


@app.route("/api/players/<player_id>/transferCard", methods=["POST"])
def api_transfer_card(player_id):
    data = request.get_json()
    to_id = data['toId'] if data.get('toId') else ""
    from_name = data['fromHand']
    to_name = data['toHand']
    from_index = data['fromIndex']
    to_index = data['toIndex']

    try:
        from_player: Player = game_service.get_player(player_id)
    except Exception as err:
        print("Problem finding 'from' player ID {}: {}".format(player_id, err))
        return ""

    try:
        if len(to_id) > 0:
            to_player: Player = game_service.get_player(to_id)
        else:
            to_player = from_player
    except Exception as err:
        print("Problem finding 'to' player ID {}: {}".format(player_id, err))
        return ""

    try:
        from_hand: Hand = from_player.get_hand_by_name(from_name)
        to_hand: Hand = to_player.get_hand_by_name(to_name)
        from_hand.transfer_card(from_index, to_hand, to_index)
        game_service.save_player(from_player)

        if from_player != to_player:
            game_service.save_player(to_player)
    except Exception as err:
        print("Problem transferring {} card to {} for player ID {}: {}".format(from_name, to_name, player_id, err))

    if from_player == to_player:
        data: str = CustomJsonEncoder().encode(from_player).replace('"_', '"')
    else:
        data: str = CustomJsonEncoder().encode([from_player, to_player]).replace('"_', '"')
    return data


@app.route("/api/players/<player_id>/discardCard", methods=["POST"])
def api_discard_card(player_id):
    data = request.get_json()
    from_name = data['fromHand']
    from_index = data['fromIndex']

    try:
        player = game_service.get_player(player_id)
    except Exception as err:
        print("Problem finding player ID {}: {}".format(player_id, err))
        return ""

    try:
        from_hand: Hand = player.get_hand_by_name(from_name)
        to_hand: Hand = game_service.discard_pile
        from_hand.transfer_card(from_index, to_hand)
        game_service.save_player(player)
    except Exception as err:
        print("Problem discarding {} card for player ID {}: {}".format(from_name, player_id, err))

    data: str = CustomJsonEncoder().encode(player).replace('"_', '"')
    return data


@app.route("/api/turn/register/<register>")
def api_turn_register(register):
    data = request.get_json()
    register = data['register']

    try:
        info = game_service.get_register_for_turn(register)
    except Exception as err:
        print("Problem getting turn info for register {}: {}".format(register, err))
        return ""

    data: str = CustomJsonEncoder().encode(info).replace('"_', '"')
    return data


@app.route("/api/players/<player_id>/throw", methods=["POST"])
def api_throw(player_id):
    data = request.get_json()
    register = data['index']

    try:
        player = game_service.get_player(player_id)
    except Exception as err:
        print("Problem finding player ID {}: {}".format(player_id, err))
        return ""

    try:
        player.registers.throw(register)
        game_service.save_player(player)
    except Exception as err:
        print("Problem changing throw value for register {}: {}".format(register, err))
        return ""

    data: str = CustomJsonEncoder().encode(player).replace('"_', '"')
    return data


if __name__ == "__main__":
    app.run(host='0.0.0.0')
