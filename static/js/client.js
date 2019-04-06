const ws = new WebSocket('ws://' + location.host + '/ws')

ws.onmessage = function (event) {
  const postsElement = document.getElementsByClassName('posts')[0]

  const postElement = document.createElement('div')
  postElement.classList.add('post')

  const data = JSON.parse(event.data)

  const time = document.createElement('span')
  time.classList.add('time')
  time.appendChild(document.createTextNode(data.datetime))
  postElement.appendChild(time)

  postElement.appendChild(document.createTextNode(' '))

  const text = document.createElement('span')
  text.classList.add('text')
  text.appendChild(document.createTextNode(data.text))
  postElement.appendChild(text)

  postsElement.appendChild(postElement)
}
