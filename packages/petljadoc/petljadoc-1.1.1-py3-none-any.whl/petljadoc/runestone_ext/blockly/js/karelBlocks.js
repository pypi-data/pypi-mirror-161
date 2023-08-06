Blockly.Blocks['move'] = {
  /**
   * Block for moving karel forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": 'напред',
      "previousStatement": null,
      "nextStatement": null,
      "colour": 250,
      "tooltip": 'Робот се помера једно поље у напред.'
    });
  }
};

Blockly.JavaScript['move'] = function (block) {
  // Generate JavaScript for moving forward.
  return 'move_forward()\n';
};

Blockly.Blocks['turn_left'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": 'лево',
      "previousStatement": null,
      "nextStatement": null,
      "colour": 250,
      "tooltip": 'Робот се окреће на лево.'
    });
  }
};

Blockly.JavaScript['turn_left'] = function (block) {
  // Generate JavaScript for moving forward.
  return 'turn_left()\n';
};
Blockly.Blocks['turn_right'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": 'десно',
      "previousStatement": null,
      "nextStatement": null,
      "colour": 250,
      "tooltip": 'Робот се окреће на десно.'
    });
  }
};

Blockly.JavaScript['turn_right'] = function (block) {
  // Generate JavaScript for moving forward.
  return 'turn_right()\n';
};

Blockly.Blocks['pick_up'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": 'узми',
      "previousStatement": null,
      "nextStatement": null,
      "colour": 250,
      "tooltip": 'Робот узима лопту са поља на коме се налази.'
    });
  }
};

Blockly.JavaScript['pick_up'] = function (block) {
  // Generate JavaScript for moving forward.
  return 'pick_up()\n';
};


Blockly.Blocks['drop_off'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": 'остави',
      "previousStatement": null,
      "nextStatement": null,
      "colour": 250,
      "tooltip": 'Робот оставља лопту.'
    });
  }
};

Blockly.JavaScript['drop_off'] = function (block) {
  // Generate JavaScript for moving forward.
  return 'drop_off()\n';
};

Blockly.Blocks['can_move'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": 'робот може напред',
      "output": "Boolean",
      "colour": 250,
      "tooltip": 'Робот одговара на питанње да ли може да направи корак напред.'
    });
  }
};

Blockly.JavaScript['can_move'] = function (block) {
  // Generate JavaScript for moving forward.
  return ['can_move()\n', Blockly.JavaScript.ORDER_FUNCTION_CALL];
};


Blockly.Blocks['balls_present'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": 'постоји лоптица',
      "output": "Boolean",
      "colour": 250,
      "tooltip": 'Робот одговара на питање да ли има лоптица на пољу на коме се налази.'
    });
  }
};

Blockly.JavaScript['balls_present'] = function (block) {
  // Generate JavaScript for moving forward.
  return ['balls_present()\n', Blockly.JavaScript.ORDER_FUNCTION_CALL];
};


Blockly.Blocks['has_balls'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": 'робот има лоптицу',
      "output": "Boolean",
      "colour": 250,
      "tooltip": 'Да ли робот има лоптице код себе.'
    });
  }
};

Blockly.JavaScript['has_balls'] = function (block) {
  // Generate JavaScript for moving forward.
  return ['has_ball()\n', Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

Blockly.Blocks['count_balls'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": 'колико лоптица има на пољу',
      "output": "Number",
      "colour": 250,
      "tooltip": 'Робот одговара на питање колико липтица има на пољу на коме се налази.'
    });
  }
};

Blockly.JavaScript['count_balls'] = function (block) {
  // Generate JavaScript for moving forward.
  return ['count_balls()\n', Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

Blockly.Blocks['count_balls_on_hand'] = {
  /**
   * Block for moving forward.
   * @this {Blockly.Block}
   */
  init: function () {
    this.jsonInit({
      "message0": 'колико лоптица има робот',
      "output": "Number",
      "colour": 250,
      "tooltip": 'Робот одговара на питање колико липтица има код себе.'
    });
  }
};

Blockly.JavaScript['count_balls_on_hand'] = function (block) {
  // Generate JavaScript for moving forward.
  return ['count_balls_on_hand()\n', Blockly.JavaScript.ORDER_FUNCTION_CALL];
};

Blockly.Blocks['karel_controls_whileUntil'] = {
  init: function () {
    this.jsonInit({
      'type': 'controls_whileUntil',
      'message0': 'Понављај све док%1',
      'args0': [
        {
          'type': 'field_dropdown',
          'name': 'KAREL_BOOL',
          'options': [
            ['робот има лопту', 'has_ball()'],
            ['постоји лопта на пољу', 'balls_present()'],
            ['робот може напред', 'can_move()'],
          ],
        },
      ],
      'message1': '%{BKY_CONTROLS_REPEAT_INPUT_DO} %1',
      'args1': [{
        'type': 'input_statement',
        'name': 'DO',
      }],
      'previousStatement': null,
      'nextStatement': null,
      'style': 'loop_blocks',
      'helpUrl': '%{BKY_CONTROLS_WHILEUNTIL_HELPURL}',
      'extensions': ['controls_whileUntil_tooltip'],
    },)
  }
}

Blockly.JavaScript['karel_controls_whileUntil'] = function (block) {
  // Do while/until loop.
  let argument0 = block.getFieldValue('KAREL_BOOL')
  let branch = Blockly.JavaScript.statementToCode(block, 'DO');
  branch = Blockly.JavaScript.addLoopTrap(branch, block);
  return 'while (' + argument0 + ') {\n' + branch + '}\n';
};




Blockly.Blocks['controls_whileUntil'] = {
  init: function () {
    this.jsonInit(  {
      'type': 'controls_whileUntil',
      'message0': '%{BKY_CONTROLS_WHILEUNTIL_OPERATOR_WHILE} %1',
      'args0': [
        {
          'type': 'input_value',
          'name': 'BOOL',
          'check': 'Boolean',
        },
      ],
      'message1': '%{BKY_CONTROLS_REPEAT_INPUT_DO} %1',
      'args1': [{
        'type': 'input_statement',
        'name': 'DO',
      }],
      'previousStatement': null,
      'nextStatement': null,
      'style': 'loop_blocks',
      'helpUrl': '%{BKY_CONTROLS_WHILEUNTIL_HELPURL}',
      'extensions': ['controls_whileUntil_tooltip'],
    },)
  }
}


Blockly.Blocks['controls_ifelse_simple'] = {
  init: function () {
    this.jsonInit( {
    'type': 'controls_ifelse',
    'message0': '%{BKY_CONTROLS_IF_MSG_IF} %1',
    'args0': [
      {
        'type': 'field_dropdown',
        'name': 'KAREL_BOOL',
        'options': [
          ['робот има лопту', 'has_ball()'],
          ['постоји лопта на пољу', 'balls_present()'],
          ['робот може напред', 'can_move()'],
        ],
      },
    ],
    'message1': '%{BKY_CONTROLS_IF_MSG_THEN} %1',
    'args1': [
      {
        'type': 'input_statement',
        'name': 'DO0',
      },
    ],
    'message2': '%{BKY_CONTROLS_IF_MSG_ELSE} %1',
    'args2': [
      {
        'type': 'input_statement',
        'name': 'ELSE',
      },
    ],
    'previousStatement': null,
    'nextStatement': null,
    'style': 'logic_blocks',
    'tooltip': '%{BKYCONTROLS_IF_TOOLTIP_2}',
    'helpUrl': '%{BKY_CONTROLS_IF_HELPURL}',
    'suppressPrefixSuffix': true,
    'extensions': ['controls_if_tooltip'],
    },)
  }
}

Blockly.Blocks['controls_if_simple'] = {
  init: function () {
    this.jsonInit( {
    'type': 'controls_ifelse',
    'message0': '%{BKY_CONTROLS_IF_MSG_IF} %1',
    'args0': [
      {
        'type': 'field_dropdown',
        'name': 'KAREL_BOOL',
        'options': [
          ['робот има лопту', 'has_ball()'],
          ['постоји лопта на пољу', 'balls_present()'],
          ['робот може напред', 'can_move()'],
        ],
      },
    ],
    'message1': '%{BKY_CONTROLS_IF_MSG_THEN} %1',
    'args1': [
      {
        'type': 'input_statement',
        'name': 'DO0',
      },
    ],
    'previousStatement': null,
    'nextStatement': null,
    'style': 'logic_blocks',
    'tooltip': '%{BKYCONTROLS_IF_TOOLTIP_2}',
    'helpUrl': '%{BKY_CONTROLS_IF_HELPURL}',
    'suppressPrefixSuffix': true,
    'extensions': ['controls_if_tooltip'],
    },)
  }
}

