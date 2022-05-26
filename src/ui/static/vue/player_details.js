const parseData = (response) => {
    var obj = {};
    if (response.status !== 200) throw Error(response.message);
    if (!response.data) return obj;

    obj = response.data;
    if (typeof obj !== 'object') {
        obj = {};
    }

    return obj;
};

const fixupPlayer = (player) => {
    if (player.program_hand && player.program_hand.cards) {
        program_hand = player.program_hand.cards;
    } else {
        program_hand = [];
    }

    if (player.power_hand && player.power_hand.cards) {
        power_hand = player.power_hand.cards;
    } else {
        power_hand = [];
    }

    registers = [];
    if (player.registers && player.registers.cards) {
        for (let i = 0; i < player.registers.cards.length; i++) {
            registers.push({
                ...player.registers.cards[i],
                locked: player.registers.locks[i],
                throw: player.registers.throws[i],
            });
        }
    }

    return [program_hand, power_hand, registers]
}

const apiGetPlayer = async (id, urlbase) => {
    try {
        const response = await axios.get(`http://${urlbase}/api/players/${id}`);

        return parseData(response);
    } catch (error) {
        console.error(error);
        return {};
    }
};

const apiDrawPowerCard = async (id, urlbase) => {
    try {
        const response = await axios.get(`http://${urlbase}/api/players/${id}/drawPowerCard`);

        return parseData(response);
    } catch (error) {
        console.error(error);
    }
};

const apiTransferCard = async (id, fromList, fromIndex, toList, toIndex, urlbase) => {
    try {
        const data = {
            fromHand: fromList,
            fromIndex: fromIndex,
            toHand: toList,
            toIndex: toIndex
        }
        const headers = {
            headers: {
                'content-type': 'application/json'
            }
        }
        const response = await axios.post(`http://${urlbase}/api/players/${id}/transferCard`, JSON.stringify(data), headers);

        return parseData(response);
    } catch (error) {
        console.error(error);
    }
};

const apiDiscardCard = async (id, fromList, fromIndex, urlbase) => {
    try {
        const data = {
            fromHand: fromList,
            fromIndex: fromIndex
        }
        const headers = {
            headers: {
                'content-type': 'application/json'
            }
        }
        const response = await axios.post(`http://${urlbase}/api/players/${id}/discardCard`, JSON.stringify(data), headers);

        return parseData(response);
    } catch (error) {
        console.error(error);
    }
};

const apiSetOrb = async (id, filename, value, urlbase) => {
    try {
        const data = {
            orb: value
        }
        const headers = {
            headers: {
                'content-type': 'application/json'
            }
        }
        const response = await axios.put(`http://${urlbase}/api/players/${id}/powerCard/${filename}`, JSON.stringify(data), headers);

        return parseData(response);
    } catch (error) {
        console.error(error);
    }
};

const apiSetNumUses = async (id, filename, value, urlbase) => {
    try {
        const data = {
            numUses: value
        }
        const headers = {
            headers: {
                'content-type': 'application/json'
            }
        }
        const response = await axios.put(`http://${urlbase}/api/players/${id}/powerCard/${filename}`, JSON.stringify(data), headers);

        return parseData(response);
    } catch (error) {
        console.error(error);
    }
};

const apiThrow = async (id, index, urlbase) => {
    try {
        const data = {
            index: index
        }
        const headers = {
            headers: {
                'content-type': 'application/json'
            }
        }
        const response = await axios.post(`http://${urlbase}/api/players/${id}/throw`, JSON.stringify(data), headers);

        return parseData(response);
    } catch (error) {
        console.error(error);
    }
};

Vue.component('player-details', {
    props: {
        id: '',
    },
    data() {
        return {
            player: {},
            power_hand: [],
            program_hand: [],
            registers: [],
            orbs: ["(none)", "1", "2", "3"],
            num_uses: ["(none)", "1", "2", "3", "4", "5"],
            // Uncomment for EC2
            hostname: "roborally.mylio-internal.com",
            url_base: `http://roborally.mylio-internal.com/static/images/`,
            //Uncomment for local
            //hostname: "localhost:5000",
            //url_base: `http://localhost:5000/static/images/`,
        };
    },
    async created() {
        await this.loadPlayer(this.id, this.hostname);
    },
    computed: {
        program_hand_filenames: function () {
            return this.program_hand.map(x => this.url_base + "program_cards/" + x.filename);
        },
        disable_ui: function () {
            let is_destroyed = this.player.damage > 9
            return this.player.powered_down || is_destroyed || !this.player.active
        }
    },
    methods: {
        async loadPlayer(id) {
            this.player = await apiGetPlayer(id, this.hostname);
            [this.program_hand, this.power_hand, this.registers] = fixupPlayer(this.player);
        },
        async drawPowerCard() {
            this.player = await apiDrawPowerCard(this.player.id, this.hostname);
            [this.program_hand, this.power_hand, this.registers] = fixupPlayer(this.player);
        },
        startDrag(evt, index, list) {
            evt.dataTransfer.dropEffect = 'copy';
            evt.dataTransfer.effectAllowed = 'copy';
            evt.dataTransfer.setData('fromList', list);
            evt.dataTransfer.setData('fromIndex', index);
        },
        async onDrop(evt, toIndex, toList) {
            const fromList = evt.dataTransfer.getData('fromList');
            const fromIndex = parseInt(evt.dataTransfer.getData('fromIndex'));

            if ((fromList == "registers" && toList == "program_hand") ||
                (fromList == "program_hand" && toList == "registers")) {
                this.player = await apiTransferCard(this.player.id, fromList, fromIndex, toList, toIndex, this.hostname);
                [this.program_hand, this.power_hand, this.registers] = fixupPlayer(this.player);
            }
        },
        async discardCard(fromIndex, fromList) {
            this.player = await apiDiscardCard(this.player.id, fromList, fromIndex, this.hostname);
            [this.program_hand, this.power_hand, this.registers] = fixupPlayer(this.player);
        },
        async setOrb(evt) {
            var value = JSON.parse(evt.target.value);
            this.player = await apiSetOrb(this.player.id, value.filename, value.index, this.hostname);
            [this.program_hand, this.power_hand, this.registers] = fixupPlayer(this.player);
        },
        async setNumUses(evt) {
            var value = JSON.parse(evt.target.value);
            this.player = await apiSetNumUses(this.player.id, value.filename, value.index, this.hostname);
            [this.program_hand, this.power_hand, this.registers] = fixupPlayer(this.player);
        },
        openInNewTab: function (url) {
            window.open(url, "_blank");
        },
        async onCheck(index) {
            this.player = await apiThrow(this.player.id, index, this.hostname);
            [this.program_hand, this.power_hand, this.registers] = fixupPlayer(this.player);
        }
    },
    template: `
    <div class="container">
        <h3>Program Card Hand</h3>
        <div class="row mb-3">
            <div class="col-lg-12 col-md-12 col-xs-3">
                <template v-if="program_hand_filenames.length > 0">
                    <span class="card-thumbnail" v-for="(filename, i) in program_hand_filenames">
                        <template v-if="disable_ui">
                            <img :src="filename" alt=""/>
                        </template>
                        <template v-else>
                            <img :src="filename" alt=""
                            draggable @dragstart="startDrag($event, i, 'program_hand')" @touchstart="startDrag($event, i, 'program_hand')" 
                            @drop="onDrop($event, i, 'program_hand')" @touchend="onDrop($event, i, 'program_hand')" 
                            @dragover.prevent @dragenter.prevent @drop.stop.prevent @touchmove.prevent/>
                        </template>
                    </span>
                </template>
                <template v-else>
                    <span class="card-thumbnail">
                        <img :src="url_base + 'card_placeholder.png'" alt=""
                        @drop="onDrop($event, 0, 'program_hand')" @touchend="onDrop($event, 0, 'program_hand')"
                         @dragover.prevent @dragenter.prevent @drop.stop.prevent @touchmove.prevent/>
                    </span>
                </template>
            </div>
        </div>

        <h3>Registers</h3>
        <div class="row">
            <div class="col-lg-12 col-md-12 col-xs-3">
                <template v-if="registers.length > 0">
                    <span class="card-thumbnail" v-for="(register, i) in registers">
                        <template v-if="disable_ui || register.locked==true">
                            <img v-if="register.filename.length > 0" :src="url_base + 'program_cards/' + register.filename" alt=""/>
                            <img v-else :src="url_base + 'card_placeholder.png'" alt=""/>
                        </template>
                        <template v-else>
                            <img v-if="register.filename.length > 0" :src="url_base + 'program_cards/' + register.filename" alt=""
                            draggable @dragstart="startDrag($event, i, 'registers')" @touchstart="startDrag($event, i, 'registers')"/>
                            <img v-else :src="url_base + 'card_placeholder.png'" alt="" 
                            @drop="onDrop($event, i, 'registers')" @touchend="onDrop($event, i, 'registers')" 
                            @dragover.prevent @dragenter.prevent @drop.stop.prevent @touchmove.prevent/>
                        </template>       
                        <p v-if="register.locked==true" class="mt-2">LOCKED</p>
                        <p v-else class="mt-2">{{i+1}}</p>
                        <span class="form-check">
                            <input class="form-check-input" type="checkbox" v-model="register.throw" @click="onCheck(i)">
                            <label class="form-check-label" for="flexCheckDefault">Throw</label>
                        </span>           
                    </span>
                </template>
                <template v-else>
                    <span>
                        None, which is a big problem.
                    </span>
               </template>
            </div>
        </div>

        <h3>Power Card Hand</h3>
        <div class="row">
            <div class="col-lg-1 centered" v-if="!disable_ui">
                <button type="button" class="btn btn-dark btn-lg" @click="drawPowerCard()">Draw</button>
            </div>
            <div class="col-lg-11 col-md-11 col-xs-2">
                <template v-if="power_hand.length > 0">
                    <template v-if="disable_ui">
                        <span class="card-thumbnail" v-for="(p_card, i) in power_hand">
                            <img  :src="url_base + 'power_cards/' + p_card.filename" alt=""
                            @click="openInNewTab(url_base + 'power_cards/' + p_card.filename)"/>
                        </span>
                    </template>
                    <template v-else>
                        <span class="card-thumbnail" v-for="(p_card, i) in power_hand">
                            <img :src="url_base + 'power_cards/' + p_card.filename" alt=""
                            @click="openInNewTab(url_base + 'power_cards/' + p_card.filename)"
                            draggable @dragstart="startDrag($event, i, 'power_hand')" @touchstart="startDrag($event, i, 'power_hand')"
                            @drop="onDrop($event, i, 'power_hand')" @touchend="onDrop($event, i, 'power_hand')" 
                            @dragover.prevent @dragenter.prevent @drop.stop.prevent @touchmove.prevent/>
                            <span>
                                Orb:
                                <select class="form-select form-select-sm" @change="setOrb($event)">
                                    <template v-for="(option, oi) in orbs">
                                        <option :key="oi" v-bind:value="JSON.stringify({filename: p_card.filename, index: oi})"
                                        :selected="oi === p_card.orb">{{ option }}</option>
                                    </template>
                                </select>
                            </span>
                            <span>
                                Uses:
                                <select class="form-select form-select-sm" @change="setNumUses($event)">
                                    <template v-for="(option, oi) in num_uses">
                                        <option :key="oi" v-bind:value="JSON.stringify({filename: p_card.filename, index: oi})"
                                        :selected="oi === p_card.num_uses">{{ option }}</option>
                                    </template>
                                </select>
                            </span>
                            <button type="button" class="mt-2 btn btn-dark btn-sm" @click="discardCard(i, 'power_hand')">Discard</button>
                        </span>
                    </template>                    
                </template>
                <template v-else>
                   <span class="card-thumbnail">
                        <img  :src="url_base + 'card_placeholder.png'" alt=""
                        @drop="onDrop($event, 0, 'power_hand')" @touchend="onDrop($event, 0, 'power_hand')" 
                        @dragover.prevent @dragenter.prevent @drop.stop.prevent @touchmove.prevent/>
                   </span>
                </template>
            </div>
        </div>   
    </div>
`,
});

new Vue({
    el: '#player-vue',
});
