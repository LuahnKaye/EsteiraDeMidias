"use client";

import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { motion } from "framer-motion";
import { ArrowRight, Star } from "lucide-react";
import useSWR from "swr";

// Register ScrollTrigger
gsap.registerPlugin(ScrollTrigger);

// Mock SWR fetcher to simulate real-time products coming from our Media Pipeline
const fetcher = async () => {
  // Simulating network delay
  await new Promise(resolve => setTimeout(resolve, 800));
  return [
    {
      id: "1",
      nome: "iPhone 15 Pro Titanium",
      preco: "R$ 7.299,00",
      vendedor: "Magalu Oficial",
      avaliacao: 4.9,
      tag: "Mais Vendido",
      imagem: "https://images.unsplash.com/photo-1696446701796-da61225697cc?q=80&w=640&auto=format&fit=crop"
    },
    {
      id: "2",
      nome: "MacBook Air M2",
      preco: "R$ 8.499,00",
      vendedor: "Apple Store",
      avaliacao: 5.0,
      tag: "Oferta",
      imagem: "https://images.unsplash.com/photo-1661961112951-f2bfd1f253ce?q=80&w=640&auto=format&fit=crop"
    },
    {
      id: "3",
      nome: "Smart TV Samsung Neo QLED 65\"",
      preco: "R$ 5.999,00",
      vendedor: "Samsung Brasil",
      avaliacao: 4.8,
      imagem: "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?q=80&w=640&auto=format&fit=crop"
    },
    {
      id: "4",
      nome: "PlayStation 5 Digital",
      preco: "R$ 3.899,00",
      vendedor: "Sony Center",
      avaliacao: 4.9,
      tag: "Estoque Baixo",
      imagem: "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?q=80&w=640&auto=format&fit=crop"
    }
  ];
};

export default function Home() {
  const heroRef = useRef(null);
  const textRef = useRef(null);
  
  // Real-time data fetching simulation
  const { data: produtos, isLoading } = useSWR('/api/produtos', fetcher, { 
    refreshInterval: 10000 // Polls every 10s to simulate live marketplace updates
  });

  useEffect(() => {
    // GSAP Parallax Animation
    const ctx = gsap.context(() => {
      gsap.fromTo(
        textRef.current,
        { y: 50, opacity: 0 },
        { y: 0, opacity: 1, duration: 1.2, ease: "power4.out", delay: 0.2 }
      );

      gsap.to(".hero-bg", {
        yPercent: 30,
        ease: "none",
        scrollTrigger: {
          trigger: heroRef.current,
          start: "top top",
          end: "bottom top",
          scrub: true,
        },
      });
    }, heroRef);

    return () => ctx.revert();
  }, []);

  return (
    <>
      {/* Hero Section */}
      <section ref={heroRef} className="relative h-[80vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0 hero-bg opacity-30">
          <div className="absolute inset-0 bg-gradient-to-b from-transparent to-magalu-dark z-10" />
          <img 
            src="https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?q=80&w=1920&auto=format&fit=crop" 
            alt="E-commerce Premium"
            className="w-full h-full object-cover"
          />
        </div>
        
        <div ref={textRef} className="relative z-10 text-center px-4 max-w-4xl mx-auto mt-[-5rem]">
          <span className="inline-block py-1 px-3 rounded-full bg-magalu-blue/20 text-magalu-blue border border-magalu-blue/30 text-sm font-medium mb-6 backdrop-blur-md">
            Marketplace de Luxo
          </span>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-6 leading-tight">
            Descubra o futuro das <span className="text-transparent bg-clip-text bg-gradient-to-r from-magalu-blue to-magalu-yellow">compras digitais</span>
          </h1>
          <p className="text-xl text-slate-400 mb-10 max-w-2xl mx-auto">
            Uma experiência construída para velocidade, segurança e design de ponta. Produtos otimizados em tempo real.
          </p>
          <div className="flex gap-4 justify-center">
            <button className="bg-magalu-blue hover:bg-blue-600 text-white px-8 py-4 rounded-full font-medium transition-all shadow-lg shadow-magalu-blue/20 flex items-center gap-2">
              Explorar Produtos <ArrowRight className="w-5 h-5" />
            </button>
            <button className="glass-card hover:bg-white/5 px-8 py-4 rounded-full font-medium transition-all">
              Seja um Vendedor
            </button>
          </div>
        </div>
      </section>

      {/* Real-time Products Section */}
      <section className="py-20 px-6 container mx-auto max-w-7xl relative z-20 bg-magalu-dark">
        <div className="flex justify-between items-end mb-12 border-b border-slate-800 pb-6">
          <div>
            <h2 className="text-3xl font-bold mb-2">Lançamentos Recentes</h2>
            <p className="text-slate-400">Atualizado em tempo real pelos nossos lojistas</p>
          </div>
          <div className="flex items-center gap-2 text-sm text-magalu-blue bg-magalu-blue/10 px-4 py-2 rounded-full">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-magalu-blue opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-magalu-blue"></span>
            </span>
            Sincronização Ao Vivo (SWR)
          </div>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[1, 2, 3, 4].map((skeleton) => (
              <div key={skeleton} className="glass-card h-[400px] animate-pulse bg-slate-800/50" />
            ))}
          </div>
        ) : (
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={{
              hidden: { opacity: 0 },
              visible: {
                opacity: 1,
                transition: { staggerChildren: 0.15 }
              }
            }}
          >
            {produtos?.map((produto) => (
              <motion.div
                key={produto.id}
                variants={{
                  hidden: { y: 40, opacity: 0 },
                  visible: { y: 0, opacity: 1, transition: { type: "spring", stiffness: 80, damping: 15 } }
                }}
                className="glass-card group flex flex-col overflow-hidden cursor-pointer"
              >
                <div className="relative h-64 overflow-hidden bg-slate-900 rounded-t-2xl">
                  {produto.tag && (
                    <div className="absolute top-4 left-4 z-10 bg-magalu-dark/80 backdrop-blur-md text-xs font-semibold px-3 py-1 rounded-full border border-white/10">
                      {produto.tag}
                    </div>
                  )}
                  <img 
                    src={produto.imagem} 
                    alt={produto.nome}
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110 opacity-90 group-hover:opacity-100"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-magalu-dark via-transparent to-transparent opacity-90" />
                </div>
                
                <div className="p-5 flex-1 flex flex-col relative z-10 bg-magalu-card/50">
                  <div className="flex items-center gap-1 mb-2 text-magalu-yellow">
                    <Star className="w-4 h-4 fill-current" />
                    <span className="text-xs font-medium text-slate-300">{produto.avaliacao}</span>
                  </div>
                  <h3 className="text-lg font-medium text-white mb-1 line-clamp-2">{produto.nome}</h3>
                  <p className="text-xs text-slate-400 mb-4 font-mono">Vendido por <span className="text-magalu-blue">{produto.vendedor}</span></p>
                  <div className="mt-auto pt-4 border-t border-slate-700/50">
                    <p className="text-2xl font-bold text-white">{produto.preco}</p>
                    <p className="text-xs text-emerald-400 mt-1 font-medium">À vista no PIX</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </section>
    </>
  );
}
