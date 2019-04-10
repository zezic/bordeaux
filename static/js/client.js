const threadSlug = document.querySelector('.thread').dataset.slug
const ws = new WebSocket('ws://' + location.host + '/ws/' + threadSlug)

ws.onmessage = function (event) {
  console.log(event)
  if (!('content' in document.createElement('template'))) {
    return
  }

  const data = JSON.parse(event.data)
  const template = document.querySelector('#post-template');

  const posts = document.querySelector('.posts');

  const clone = document.importNode(template.content, true);
  clone.querySelector('.datetime').textContent = data.datetime;
  const offset = '0x' + data.offset.toString(16)
  clone.querySelector('.id').href += offset
  clone.querySelector('.id').appendChild(document.createTextNode(offset))
  clone.querySelector('.body').innerHTML = data.html
  clone.querySelector('.body').querySelectorAll('pre code').forEach((block) => {
    hljs.highlightBlock(block)
  })

  posts.appendChild(clone)
}
