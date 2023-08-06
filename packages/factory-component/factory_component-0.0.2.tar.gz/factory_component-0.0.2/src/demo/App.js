/* eslint no-magic-numbers: 0 */
import React, { Component, useState } from 'react';
// import { ResizableBox } from 'react-resizable';
import './handle.css';
import './style.css';
// import Editor from "@monaco-editor/react";
import { TextEditor } from '../lib';
// import { Rnd } from '../lib';


class App extends Component {

    constructor() {
        super();
        this.state = {
            width: 30,
            height: 30,
        };
        this.setProps = this.setProps.bind(this);
    }

    setProps(newProps) {
        this.setState(newProps);
    }

    render() {
        return (
            <TextEditor
                    // height="90vh"
                    // width="90vw"
                    defaultLanguage="javascript"
                    defaultValue="// let's write some broken code 😈"
            />
        );
    }
}

export default App;
