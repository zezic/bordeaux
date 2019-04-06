const ws = new WebSocket('ws://' + location.host + '/ws')

ws.onmessage = function (event) {
  const postsElement = document.getElementsByClassName('posts')[0]
  const postElement = document.createElement('p')
  const text = document.createTextNode(event.data)
  postElement.appendChild(text)
  postsElement.appendChild(postElement)
}
