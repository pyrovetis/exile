stickyHeader()
stickyMenu()

dashboardMenuMaxHeightSetter()
window.addEventListener('resize', dashboardMenuMaxHeightSetter)

function stickyHeader() {
    const header = document.querySelector('.primary-header')
    const scrollWatcher = document.querySelectorAll("[data-scroll-watcher]")[0];

    const headerObserver = new IntersectionObserver((entries) => {
        header.classList.toggle('is-fixed', !entries[0].isIntersecting)
    })

    headerObserver.observe(scrollWatcher)
}

function stickyMenu() {
    const breadcrumbs = document.querySelector('.breadcrumbs')
    const scrollWatcher = document.querySelectorAll("[data-scroll-watcher]")[1];

    const headerObserver = new IntersectionObserver((entries) => {
        breadcrumbs.classList.toggle('is-sticky', !entries[0].isIntersecting)
    }, {rootMargin: '33px 0px 0px 0px'})

    if (scrollWatcher) {
        headerObserver.observe(scrollWatcher)
    }
}


function dashboardMenuMaxHeightSetter() {
    const dashboardMenu = document.querySelector('.dashboard-menu')
    const header = document.querySelector('.primary-header')
    const screenHeight = window.innerHeight
    const headerHeight = header.clientHeight
    if (dashboardMenu) {
        dashboardMenu.style.setProperty('--max-height', `${screenHeight - headerHeight - 8}px`)
    }
}

document.addEventListener('alpine:init', () => {
    Alpine.store('notes', {
        on: false,
        text: "",
        toggle() {
            this.on = !this.on
        }
    })
})

function handleCopy(e, origin) {
    navigator.clipboard.writeText(`https://exile.ir/${origin}`)
    e.target.setAttribute("data-tooltip", "Copied!")
    setTimeout(() => e.target.removeAttribute("data-tooltip"), 1000)
}

var switchButton = document.querySelector("input.theme-toggle");
switchButton.addEventListener("click", () => toggleTheme());