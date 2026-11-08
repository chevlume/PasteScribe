const React = require('react');
const ReactDOM = require('react-dom');
const { Editor, EditorState } = require('draft-js');
function App() {
  const [state, setState] = React.useState(() => EditorState.createEmpty());
  window.__getText = () => state.getCurrentContent().getPlainText('\n');
  return React.createElement('div', null,
    React.createElement('div', { id: 'box', style: { border: '1px solid #999', minHeight: 120, width: 600, padding: 8 } },
      React.createElement(Editor, { editorState: state, onChange: setState, placeholder: 'What is happening?' })));
}
ReactDOM.render(React.createElement(App), document.getElementById('root'));
