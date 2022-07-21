const getPowerCardsAndRegisters = (player) => {
    var power_hand = [];
    if (player.power_hand && player.power_hand.cards) {
        power_hand = player.power_hand.cards;
    }

    var reges = [];
    if (player.registers && player.registers.cards) {
        for (let i = 0; i < player.registers.cards.length; i++) {
            reges.push({
                ...player.registers.cards[i],
                locked: player.registers.locks[i],
                throw: player.registers.throws[i],
            });
        }
    }

    return {
        id: player.id,
        name: player.name,
        power_hand: power_hand,
        registers: reges,
    }
}

const apiGetPlayers = async (urlbase) => {
    try {
        const response = await axios.get(`http://${urlbase}/api/players`);

        return parseData(response);
    } catch (error) {
        console.error(error);
        return [];
    }
};

const apiTransferCardBetweenPlayers = async (fromId, fromIndex, toId, toIndex, urlbase) => {
    try {
        const data = {
            fromHand: "power_hand",
            fromIndex: fromIndex,
            toId: toId,
            toHand: "power_hand",
            toIndex: toIndex
        }
        const headers = {
            headers: {
                'content-type': 'application/json'
            }
        }
        const response = await axios.post(`http://${urlbase}/api/players/${fromId}/transferCard`, JSON.stringify(data), headers);
        const players = parseData(response);

        return [players[0], players[1]];
    } catch (error) {
        console.error(error);
    }
};

const apiDiscardCardById = async (fromId, fromIndex, urlbase) => {
    try {
        const data = {
            fromHand: "power_hand",
            fromIndex: fromIndex
        }
        const headers = {
            headers: {
                'content-type': 'application/json'
            }
        }
        const response = await axios.post(`http://${urlbase}/api/players/${fromId}/discardCard`, JSON.stringify(data), headers);

        return parseData(response);
    } catch (error) {
        console.error(error);
    }
};

const updatePlayer = function (player, players) {
    for (var i = 0; i < players.length; i++) {
        if (players[i].id === player.id) {
            Vue.set(players, i, getPowerCardsAndRegisters(player));
            break;
        }
    }
}

Vue.component('public-cards', {
    data() {
        return {
            players: [],
            // Uncomment for EC2
            hostname: "roborally.mylio-internal.com",
            url_base: `http://roborally.mylio-internal.com/static/images/`,
            //Uncomment for local
            //hostname: "localhost:5000",
            //url_base: `http://localhost:5000/static/images/`,
            orbs: ["(none)", "1", "2", "3"],
            num_uses: ["(none)", "1", "2", "3", "4", "5", "6", "7"],
        };
    },
    async created() {
        await this.loadPlayers();
    },
    methods: {
        async loadPlayers() {
            var players = await apiGetPlayers(this.hostname);
            players.map(x => this.players.push(getPowerCardsAndRegisters(x)));
        },
        async drawPowerCard(id) {
            var player = await apiDrawPowerCard(id, this.hostname);
            updatePlayer(player, this.players);
        },
        startDrag(evt, index, id) {
            evt.dataTransfer.dropEffect = 'copy';
            evt.dataTransfer.effectAllowed = 'copy';
            evt.dataTransfer.setData('fromId', id);
            evt.dataTransfer.setData('fromIndex', index);
        },
        async onDrop(evt, toIndex, toId) {
            const fromId = evt.dataTransfer.getData('fromId');
            const fromIndex = parseInt(evt.dataTransfer.getData('fromIndex'));

            var [fromPlayer, toPlayer] = await apiTransferCardBetweenPlayers(fromId, fromIndex, toId, toIndex, this.hostname);
            updatePlayer(fromPlayer, this.players);
            updatePlayer(toPlayer, this.players);
        },
        async discardCard(fromIndex, fromId) {
            var player = await apiDiscardCardById(fromId, fromIndex, this.hostname);
            updatePlayer(player, this.players);
        },
        async setOrb(evt) {
            var value = JSON.parse(evt.target.value);
            var player = await apiSetOrb(value.id, value.filename, value.index, this.hostname);
            updatePlayer(player, this.players);
        },
        async setNumUses(evt) {
            var value = JSON.parse(evt.target.value);
            var player = await apiSetNumUses(value.id, value.filename, value.index, this.hostname);
            updatePlayer(player, this.players);
        },
        openInNewTab: function (url) {
            window.open(url, "_blank");
        }
    },
    template: `
        <div class="container">
            <div class="row" v-for="(player, i) in players" :key="player.id">
                <div class="col-lg-2 centered">
                    {{ player.name }}
                </div>
                <div class="col-lg-1 centered" >
                    <button type="button" class="btn btn-dark btn-lg" @click="drawPowerCard(player.id)">Draw</button>
                </div>
                <div class="col-lg-4 col-md-4 col-xs-2">
                    <template v-if="player.power_hand.length > 0">
                        <span class="card-thumbnail" v-for="(p_card, i) in player.power_hand">
                            <img  :src="url_base + 'power_cards/' + p_card.filename" alt=""
                            @click="openInNewTab(url_base + 'power_cards/' + p_card.filename)"
                            draggable @dragstart="startDrag($event, i, player.id)" @touchstart="startDrag($event, i, player.id)"
                            @drop="onDrop($event, i, player.id)" @touchend="onDrop($event, i, player.id)" 
                            @dragover.prevent @dragenter.prevent @drop.stop.prevent @touchmove.prevent/>
                            <span>
                                Orb:
                                <select class="form-select form-select-sm" @change="setOrb($event)">
                                    <template v-for="(option, oi) in orbs">
                                        <option :key="oi" v-bind:value="JSON.stringify({id: player.id, filename: p_card.filename, index: oi})"
                                        :selected="oi === p_card.orb">{{ option }}</option>
                                    </template>
                                </select>
                            </span>
                            <span>
                                Uses:
                                <select class="form-select form-select-sm" @change="setNumUses($event)">
                                    <template v-for="(option, oi) in num_uses">
                                        <option :key="oi" v-bind:value="JSON.stringify({id: player.id, filename: p_card.filename, index: oi})"
                                        :selected="oi === p_card.num_uses">{{ option }}</option>
                                    </template>
                                </select>
                            </span>
                            <button type="button" class="mt-2 btn btn-dark btn-sm" @click="discardCard(i, player.id)">Discard</button>
                        </span>                  
                    </template>
                    <template v-else>
                        <span class="card-thumbnail">
                            <img  :src="url_base + 'card_placeholder.png'" alt=""
                            @drop="onDrop($event, 0, player.id)" @touchend="onDrop($event, 0, player.id)" 
                            @dragover.prevent @dragenter.prevent @drop.stop.prevent @touchmove.prevent/>
                        </span>
                    </template>
                </div>
                <div class="col-lg-5">
                    <span class="card-thumbnail" v-for="(register, i) in player.registers">
                        <template v-if="register.locked==true">
                            <img :src="url_base + 'program_cards/' + register.filename" alt="" 
                             @click="openInNewTab(url_base + 'program_cards/' + register.filename)"/>
                        </template>
                        <template v-else>
                            <img :src="url_base + 'card_placeholder.png'" alt="" />
                        </template>       
                        <p class="mt-2">{{i+1}}</p>         
                    </span>
                </div>
                <hr/>
            </div>
        </div>
`,
});

new Vue({
    el: '#public-cards-vue',
});
