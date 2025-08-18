'use client'

import Script from 'next/script'

export default function Home() {
  return (
    <div className="bg-[#0b0d12] text-slate-200 antialiased">
      <div className="pointer-events-none fixed inset-0 -z-10">
        <div className="absolute inset-0 bg-[radial-gradient(1200px_600px_at_20%_-10%,rgba(76,29,149,0.15),transparent),radial-gradient(900px_500px_at_80%_-10%,rgba(2,132,199,0.12),transparent)]"></div>
        <canvas id="bg3d" className="absolute inset-0 opacity-70"></canvas>
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-slate-700/40 to-transparent"></div>
      </div>

      <header className="sticky top-0 z-50 backdrop-blur supports-[backdrop-filter]:bg-slate-900/50">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <a href="#" className="group inline-flex items-center gap-3">
              <div className="grid h-8 w-8 place-items-center rounded-md border border-slate-700/70 bg-slate-900 shadow-sm ring-1 ring-black/5">
                <span className="text-[11px] font-semibold tracking-tight text-slate-100">SMAI</span>
              </div>
              <span className="text-sm font-medium text-slate-300 group-hover:text-slate-200 transition-colors">Social Media AI Platform</span>
            </a>
            <nav className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm text-slate-400 hover:text-slate-200 transition-colors">Features</a>
              <a href="#agents" className="text-sm text-slate-400 hover:text-slate-200 transition-colors">Agents</a>
              <a href="#analytics" className="text-sm text-slate-400 hover:text-slate-200 transition-colors">Analytics</a>
              <a href="#docs" className="text-sm text-slate-400 hover:text-slate-200 transition-colors">Docs</a>
              <a href="#install" className="text-sm text-slate-400 hover:text-slate-200 transition-colors">Install</a>
            </nav>
            <div className="hidden md:flex items-center gap-3">
              <a href="https://github.com/DavidLai82/socialmediaapp" target="_blank" className="inline-flex items-center gap-2 rounded-md border border-slate-700/70 bg-slate-900 px-3 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800 hover:border-slate-600 transition-colors">
                <i data-lucide="github" className="h-4 w-4"></i>
                <span>GitHub</span>
              </a>
              <a href="#get-started" className="inline-flex items-center gap-2 rounded-md bg-indigo-600 px-3.5 py-2 text-sm font-semibold text-white hover:bg-indigo-500 transition-colors shadow-sm ring-1 ring-indigo-500/20">
                <i data-lucide="rocket" className="h-4 w-4"></i>
                <span>Get Started</span>
              </a>
            </div>
            <button id="mobileMenuBtn" className="md:hidden inline-flex items-center justify-center rounded-md border border-slate-700/70 bg-slate-900 p-2 text-slate-200 hover:bg-slate-800 hover:border-slate-600 transition-colors" aria-expanded="false" aria-controls="mobileMenu">
              <i data-lucide="menu" className="h-5 w-5"></i>
            </button>
          </div>
          <div id="mobileMenu" className="md:hidden hidden border-t border-slate-800/80">
            <div className="flex flex-col gap-1 py-3">
              <a href="#features" className="px-2 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-800/60 rounded">Features</a>
              <a href="#agents" className="px-2 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-800/60 rounded">Agents</a>
              <a href="#analytics" className="px-2 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-800/60 rounded">Analytics</a>
              <a href="#docs" className="px-2 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-800/60 rounded">Docs</a>
              <a href="#install" className="px-2 py-2 text-sm text-slate-300 hover:text-white hover:bg-slate-800/60 rounded">Install</a>
              <div className="flex items-center gap-2 px-2 pt-2">
                <a href="https://github.com/DavidLai82/socialmediaapp" target="_blank" className="flex-1 inline-flex items-center justify-center gap-2 rounded-md border border-slate-700/70 bg-slate-900 px-3 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800 transition-colors">
                  <i data-lucide="github" className="h-4 w-4"></i>
                  <span>GitHub</span>
                </a>
                <a href="#get-started" className="flex-1 inline-flex items-center justify-center gap-2 rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white hover:bg-indigo-500 transition-colors">
                  <i data-lucide="rocket" className="h-4 w-4"></i>
                  <span>Start</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* ... (rest of provided sections omitted for brevity) ... */}

      <Script src="https://unpkg.com/lucide@latest" strategy="afterInteractive" />
      <Script src="https://cdn.jsdelivr.net/npm/chart.js" strategy="afterInteractive" />
      <Script id="landing-inline" strategy="afterInteractive">{`
        document.body.style.fontFamily = 'Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, "Helvetica Neue", Arial, "Noto Sans", "Apple Color Emoji", "Segoe UI Emoji"';
        if (window.lucide) { window.lucide.createIcons({ attrs: { 'stroke-width': 1.5 } }); }
      `}</Script>
    </div>
  )
}