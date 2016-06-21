/**
 * Resize an iframe to its content
 * @param  {Element} iframe a loaded iframe
 */
function resizeIframe(iframe) {
    iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
}
