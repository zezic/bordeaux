const threadSlug = document.querySelector('.thread').dataset.slug
const ws = new WebSocket('ws://' + location.host + '/ws/' + threadSlug)

function addOffsetQuoteToWriter (offset) {
  const writer = document.querySelector('.writer-wrapper')
  const textarea = writer.querySelector('textarea')
  const value = textarea.value
  const toAdd = ':' + offset

  // save selection start and end position
  const start = textarea.selectionStart
  const end = textarea.selectionEnd

  // update the value with our text inserted
  textarea.value = value.slice(0, start) + toAdd + value.slice(end)

  // update cursor to be at the end of insertion
  textarea.selectionStart = textarea.selectionEnd = start + toAdd.length
}

function placeWriterAfterPost (post) {
  const flipping = new Flipping()
  const posts = post ? post.parentNode : document.querySelector('.thread .posts')
  const next = post ? post.nextSibling : posts.firstChild
  const writer = document.querySelector('.writer-wrapper')
  if (!next || !next.classList || !next.classList.contains('writer-wrapper')) {
    flipping.read()
    writer.remove()
    posts.insertBefore(writer, next)
    flipping.flip()
  }
  const textarea = writer.querySelector('textarea')
  setTimeout(() => {
    textarea.focus()
  }, 600)
}

function addListeners (post) {
  const offset = post.querySelector('.offset')
  offset.addEventListener('click', (event) => {
    event.preventDefault()
    addOffsetQuoteToWriter(post.id)
    placeWriterAfterPost(post)
  })
}

document.querySelectorAll('.thread .post').forEach((post) => {
  addListeners(post)
})

document.querySelector('.common-layout .header .thread-slug').addEventListener('click', (event) => {
  event.preventDefault()
  addOffsetQuoteToWriter('0x0')
  placeWriterAfterPost(null)
})

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
  clone.querySelector('.offset').href += offset
  clone.querySelector('.offset').appendChild(document.createTextNode(offset))
  clone.querySelector('.post').id = offset
  clone.querySelector('.post').dataset.flipKey += data.offset
  clone.querySelector('.body').innerHTML = data.html
  clone.querySelector('.body').querySelectorAll('pre code').forEach((block) => {
    hljs.highlightBlock(block)
  })
  addListeners(clone.querySelector('.post'))

  posts.appendChild(clone)
}
