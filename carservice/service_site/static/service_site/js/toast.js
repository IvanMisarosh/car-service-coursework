const toastTemplate = document.querySelector("[data-toast-template]")
const toastContainer = document.querySelector("[data-toast-container]")

function createToast(message) {
    // Clone the template
    const element = toastTemplate.cloneNode(true)
    delete element.dataset.toastTemplate
    toastContainer.appendChild(element)

    // Add default class or use tags to decide styling
    if (message.tags && message.tags.includes("error")) {
        element.classList.add("bg-danger", "text-white");
    } else if (message.tags && message.tags.includes("success")) {
        element.classList.add("bg-success", "text-white");
    } else {
        // Apply other tags as-is
        element.className += " " + message.tags;
    }

    element.querySelector("[data-toast-body]").innerText = message.message

    const toast = new bootstrap.Toast(element, {delay: 2000})
    toast.show()
  }


htmx.on("messages", (e) => {
  console.log('messages', e.detail.value)
  e.detail.value.forEach(createToast)
})