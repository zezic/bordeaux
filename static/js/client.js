const threadSlug = document.querySelector('.thread').dataset.slug
const ws = new WebSocket('ws://' + location.host + '/ws/' + threadSlug)

function addOffsetQuoteToWriter (offset) {
  const writer = document.querySelector('.writer-wrapper')
  const textarea = writer.querySelector('textarea')
  const value = textarea.value
  const toAdd = ':' + offset + ' '

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
  if (offset) {
    offset.addEventListener('click', (event) => {
      event.preventDefault()
      addOffsetQuoteToWriter(post.id)
      placeWriterAfterPost(post)
    })
  }
  post.querySelectorAll('.brdx-link-wrapper').forEach((linkWrp) => {
    const targetId = linkWrp.querySelector('a').dataset.post
    const selector = '.post[data-id="' + targetId + '"]'
    const targetPost = document.querySelectorAll(selector)[0]
    linkWrp.addEventListener('mouseenter', (event) => {
      showQuotedPost(event.target, targetPost)
    })
    linkWrp.addEventListener('mouseleave', (event) => {
      hideQuotedPost(event.target)
    })
  })
}

function showQuotedPost (linkWrp, post) {
  let clone = linkWrp.querySelector('.post')
  if (!clone) {
    clone = post.cloneNode(true)
    clone.style.left = ''
    clone.querySelectorAll('.brdx-link-wrapper > .post').forEach((postClone) => {
      postClone.remove()
    })
    clone.classList.add('transparent')
    addListeners(clone)
    linkWrp.classList.add('expanded')
    linkWrp.appendChild(clone)
    const rect = clone.getBoundingClientRect()
    if (rect.bottom > window.innerHeight) {
      clone.classList.add('up')
    }
    if (rect.right > window.innerWidth) {
      clone.style.left = (window.innerWidth - rect.right - 20).toString() + 'px'
    }
    clone.classList.remove('transparent')
  }
}
function hideQuotedPost (linkWrp) {
  clone = linkWrp.querySelector('.post')
  setTimeout(() => {
    clone.remove()
    linkWrp.classList.remove('expanded')
  }, 500)
}

function extractBRDXLinks (post) {
  const postLinkWrp = document.createElement('div')
  postLinkWrp.classList.add('brdx-link-wrapper')
  const postLink = document.createElement('a')
  postLink.href = '#' + post.id
  postLink.dataset.post = post.id
  postLink.classList.add('brdx-link', 'pst')
  postLink.innerHTML = '<span>:</span>' + post.id
  postLinkWrp.appendChild(postLink)
  const targetPostIds = []
  post.querySelectorAll('.body .brdx-link-wrapper').forEach((linkWrp) => {
    const link = linkWrp.querySelector('a')
    if (!link.dataset.post) { return }
    if (link.dataset.thread && link.dataset.thread !== threadSlug) { return }
    const targetId = link.dataset.post
    if (targetPostIds.indexOf(targetId) !== -1) { return }
    const selector = '.post[data-id="' + targetId + '"]'
    const targetPost = document.querySelectorAll(selector)[0]
    targetPost.querySelector('.replies').appendChild(postLinkWrp)
    targetPostIds.push(targetId)
  })
}

document.querySelectorAll('.thread .post').forEach((post) => {
  extractBRDXLinks(post)
})
document.querySelectorAll('.thread .post').forEach((post) => {
  addListeners(post)
})
extractBRDXLinks(document.querySelector('.common-layout .top .post'))
addListeners(document.querySelector('.common-layout .top .post'))

document.querySelector('.common-layout .header .thread-slug').addEventListener('click', (event) => {
  event.preventDefault()
  addOffsetQuoteToWriter('0x0')
  placeWriterAfterPost(null)
})

if (document.location.href.indexOf('---') !== -1) {
  history.replaceState(
    {},
    document.title,
    document.location.href.replace('---', document.querySelector('.board-slug').innerText)
  )
}

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
  extractBRDXLinks(clone.querySelector('.post'))
  addListeners(clone.querySelector('.post'))

  posts.appendChild(clone)
}
