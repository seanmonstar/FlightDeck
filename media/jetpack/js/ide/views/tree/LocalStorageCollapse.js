var Class = require('shipyard/class/Class'),
    PersistantCollapse = require('./PersistantCollapse'),
    dom = require('shipyard/dom');

var localStorage = dom.window.get('localStorage');

module.exports = new Class({

    Extends: PersistantCollapse,

    getState: function(){
        var self = this;
        try {
            return JSON.decode(localStorage.getItem(self.key)) || {};
        } catch (jsonError) {
            return {};
        }
    },

    setState: function(element, state){
        this.parent(element, state);
        localStorage.setItem(this.key, JSON.encode(this.state));
        return this;
    }

});