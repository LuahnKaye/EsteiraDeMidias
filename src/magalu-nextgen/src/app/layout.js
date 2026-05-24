import { Inter } from "next/font/google";
import "./globals.css";
import { ShoppingCart, Search, User } from "lucide-react";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Magalu 2.0 | Next-Gen E-commerce",
  description: "A premium e-commerce experience",
};

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body className={`${inter.className} bg-magalu-dark text-slate-100`}>
        {/* Premium Navbar */}
        <nav className="glass-nav py-4 px-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-magalu-blue to-magalu-yellow flex items-center justify-center font-bold text-xl shadow-lg shadow-magalu-blue/20">
              M
            </div>
            <span className="text-2xl font-bold tracking-tight">Magalu<span className="text-magalu-blue">.io</span></span>
          </div>
          
          <div className="hidden md:flex flex-1 max-w-xl mx-8 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
            <input 
              type="text" 
              placeholder="Pesquisar produtos premium..." 
              className="w-full bg-slate-800/50 border border-slate-700 rounded-full py-2.5 pl-12 pr-4 focus:outline-none focus:border-magalu-blue focus:ring-1 focus:ring-magalu-blue transition-all"
            />
          </div>

          <div className="flex items-center gap-6">
            <button className="flex flex-col items-center gap-1 text-slate-300 hover:text-white transition-colors">
              <User className="w-6 h-6" />
              <span className="text-xs font-medium">Entrar</span>
            </button>
            <button className="relative flex flex-col items-center gap-1 text-slate-300 hover:text-white transition-colors">
              <ShoppingCart className="w-6 h-6" />
              <span className="text-xs font-medium">Sacola</span>
              <span className="absolute -top-1 -right-2 bg-magalu-blue text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">3</span>
            </button>
          </div>
        </nav>

        <main className="min-h-screen">
          {children}
        </main>

        <footer className="border-t border-slate-800 py-12 mt-20 bg-slate-900/50">
          <div className="container mx-auto px-6 text-center text-slate-500">
            <p>© 2026 Magalu 2.0 Next-Gen Marketplace. Todos os direitos reservados.</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
