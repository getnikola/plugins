const MASTODON_ACCOUNT_ID = '109270094542366763'
const MASTODON_HOST = 'nerdculture.de'

// Copies the text from an element to the clipboard, and flashes the element to provide visual feedback
async function copyElementTextToClipboard(e)
{
    const text = e.textContent
    await navigator.clipboard.writeText(text)

    e.classList.add('tootClick');
    setTimeout(() => {
        e.classList.remove('tootClick');
    }, 600);
}

// sanitise text content for display
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// renders the content - provides an array of toots, the element to add the content to and whether to show a copyable link for replies
function renderMastodonContent(toots, parentElement, showLink) {
    // clear the parent element so that we can add the new content
    parentElement.innerHTML = ''
    // add a simple "no comments" message if there are no toots
    if (!Array.isArray(toots) || toots.length === 0) {
        document.getElementById('mastodon-comments-list').innerHTML = "<div class='mastodon-comment'>No comments (yet)!</div>"
        return
    }

    // render each toot
    for (const toot of toots) {
        if (toot.sensitive) {
            // don't display toots marked as sensitive
            continue
        }

        // sanitise the toot content for display, including correctly rendering custom emojis
        toot.account.display_name = escapeHtml(toot.account.display_name)
        toot.account.emojis.forEach(emoji => {
            toot.account.display_name = toot.account.display_name.replace(`:${emoji.shortcode}:`,
                `<img src="${escapeHtml(emoji.static_url)}" alt="Emoji ${emoji.shortcode}" class="mastodon-emoji" />`);
        })
        toot.emojis.forEach(emoji => {
            toot.content = toot.content.replace(`:${emoji.shortcode}:`,
                `<img src="${escapeHtml(emoji.static_url)}" alt="Emoji ${emoji.shortcode}" class="mastodon-emoji" />`);
        })

        // create a block of HTML content including the toot data
        const comment =
            `<div class="mastodon-comment">
               <div class="mastodon-avatar">
                 <img src="${escapeHtml(toot.account.avatar_static)}" height=60 width=60 alt="${escapeHtml(toot.account.display_name)}'s avatar">
               </div>
               <div class="mastodon-body">
                 <div class="mastodon-meta">
                   <div class="mastodon-author">
                     <div class="mastodon-author-link">
                       <a href="${toot.account.url}" target="_blank" rel="nofollow">
                         <span>${toot.account.display_name}</span>
                       </a>
                       <br/>
                       <span class="mastodon-author-uid">(@${escapeHtml(toot.account.acct === 's' ? 's@sd.ai' : toot.account.acct)})</span>
                     </div>
                   </div>
                   <div class="toot-link">
                     <a class="date" href="${toot.uri}" rel="nofollow" target="_blank">
                      ${toot.created_at.substring(0, 10)}
                    </a>
                    <br/>
                  </div>
                 </div>
                 <div class="mastodon-comment-content">
                   ${toot.content}
                   <span class="tootlink" ${showLink ? '' : 'style="display: none;"'}>${toot.uri}</span>
                 </div>
              </div>
            </div>`

        // Use DOMPurify to create a sanitised element for the toot
        const child = DOMPurify.sanitize(comment, {'RETURN_DOM_FRAGMENT': true});

        // make all toot links clickable
        const links = child.querySelectorAll('.tootlink');
        for (const link of links) {
            link.onclick = function() { return copyElementTextToClipboard(this); }
        }

        // insert the toot into the DOM
        parentElement.appendChild(child);
    }
}

// We set this in the "code injection" footer for any page for which we want to enable comments
let MASTODON_POST_ID

// when the page has finished loading, send a request for the toots
document.addEventListener("DOMContentLoaded", async (event) => {
    let url, isComments
    // if we're being crawled, don't render comments - may help against spam
    const isBot = /bot|google|baidu|bing|msn|teoma|slurp|yandex/i
        .test(navigator.userAgent)

    // if there is a sidebar, we're expecting to load the toots from the main account
    if (document.getElementsByClassName('gh-sidebar').length > 0) {
        url = `https://${MASTODON_HOST}/api/v1/accounts/${MASTODON_ACCOUNT_ID}/statuses?exclude_replies=true&exclude_reblogs=true`
    }
    // if there's a post ID and we're not a bot, we're expecting to load the replies from a specific toot
    if (MASTODON_POST_ID && !isBot) {
        url = `https://${MASTODON_HOST}/api/v1/statuses/${MASTODON_POST_ID}/context`
        isComments = true
    }
    // find the element to append the content to - if there isn't one, we don't need to query
    const element = document.getElementById('mastodon-comments-list')
    if (url && element) {
        // populate the link to the source toot, if necessary (for replies)
        const linkElement = document.getElementById('toot-link-top')
        const clipElement = document.getElementById('toot-link-clip')
        const tootUrl = `https://${MASTODON_HOST}/@s/${MASTODON_POST_ID}`
        if (linkElement) {
            linkElement.href = tootUrl
        }
        if (clipElement) {
            clipElement.innerText = tootUrl
        }
        // fetch the data from Mastodon
        const response = await fetch(url)
        let content = await response.json()
        if (isComments) {
            content = content.descendants
        }
        // render the content into the page
        const header = document.getElementById('mastodon-comments-header')
        if (header) {
            header.style.display = ''
        }
        return renderMastodonContent(content, element, isComments)
    }
})
