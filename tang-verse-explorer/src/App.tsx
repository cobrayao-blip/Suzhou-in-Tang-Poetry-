import { useState, useMemo, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  Search, 
  Map as MapIcon, 
  Users, 
  BookOpen, 
  Settings, 
  ChevronRight, 
  Sparkles,
  Upload,
  Compass as SuzhouIcon,
  Navigation,
  Globe,
  ArrowUpRight,
  Hash,
  Link2,
  Wind
} from 'lucide-react';
import { cn } from '@/src/lib/utils';
import { Poem, PoemMetadata, SpatialHub, ThemeConfig } from './types';

// Sample Data
const SPATIAL_HUBS: SpatialHub[] = [
  {
    name: '寒山寺',
    poemCount: 126,
    imagery: ['钟声', '夜泊', '客愁', '明月'],
    people: ['张继', '韦应物', '白居易'],
    relatedSpaces: ['枫桥', '运河', '姑苏城'],
    description: '位于苏州城西，运河之畔，因张继《枫桥夜泊》而名垂千古。'
  },
  {
    name: '黄鹤楼',
    poemCount: 215,
    imagery: ['孤帆', '白云', '长江', '鹦鹉洲'],
    people: ['崔颢', '李白', '孟浩然'],
    relatedSpaces: ['夏口', '晴川阁', '扬州'],
    description: '江南三大名楼之首，崔颢题诗使李白也为之搁笔。'
  },
  {
    name: '曲江池',
    poemCount: 384,
    imagery: ['流觞', '柳絮', '进士', '杏园'],
    people: ['杜甫', '白居易', '韩愈'],
    relatedSpaces: ['慈恩寺', '芙蓉园', '长安'],
    description: '长安城的盛世缩影，文人雅士宴饮吟诗的绝佳去处。'
  },
  {
    name: '洞庭湖',
    poemCount: 198,
    imagery: ['银盘', '君山', '秋月', '渔翁'],
    people: ['刘禹锡', '杜甫', '李攀龙'],
    relatedSpaces: ['岳阳楼', '潇湘', '长江'],
    description: '八百里洞庭，气象万千，尽显自然之伟力。'
  }
];

const SAMPLE_POEMS: Poem[] = [
  {
    id: '1',
    title: '枫桥夜泊',
    author: '张继',
    volume: 242,
    content: '月落乌啼霜满天，江枫渔火对愁眠。\n姑苏城外寒山寺，夜半钟声到客船。',
    metadata: {
      imagery: ['月', '乌', '霜', '渔火', '钟声'],
      places: [
        { name: '姑苏', description: '苏州的古称', isSuzhouRelated: true, coordinates: { lat: 31.299, lng: 120.585 } },
        { name: '寒山寺', description: '著名的佛教寺院', isSuzhouRelated: true, coordinates: { lat: 31.311, lng: 120.575 } },
        { name: '枫桥', description: '运河上的古桥', isSuzhouRelated: true, coordinates: { lat: 31.314, lng: 120.572 } }
      ],
      relationships: [],
      suzhouElements: ['寒山寺', '枫桥', '客船'],
      summary: '描写秋夜泊舟枫桥所得的情景和感受。',
      coordinates: { lat: 31.314, lng: 120.572 }
    }
  },
  {
    id: '2',
    title: '静夜思',
    author: '李白',
    volume: 164,
    content: '床前明月光，疑是地上霜。\n举头望明月，低头思故乡。',
    metadata: {
      imagery: ['月光', '霜', '故乡'],
      places: [],
      relationships: [],
      suzhouElements: [],
      summary: '描写诗人在寂静的夜晚望月思乡的情感。',
      coordinates: { lat: 34.263, lng: 108.948 } // Xi'an (Chang'an) for mock
    }
  },
  {
    id: '3',
    title: '宿建德江',
    author: '孟浩然',
    volume: 160,
    content: '移舟泊烟渚，日暮客愁新。\n野旷天低树，江清月近人。',
    metadata: {
      imagery: ['烟渚', '日暮', '月', '客愁', '秋江'],
      places: [{ name: '建德江', description: '新安江流经建德的一段', isSuzhouRelated: false }],
      relationships: [],
      suzhouElements: [],
      summary: '描写秋江暮色中的羁旅之思。',
      coordinates: { lat: 29.474, lng: 119.281 }
    }
  },
  {
    id: '4',
    title: '江雪',
    author: '柳宗元',
    volume: 352,
    content: '千山鸟飞绝，万径人踪灭。\n孤舟蓑笠翁，独钓寒江雪。',
    metadata: {
      imagery: ['千山', '孤舟', '寒江', '雪', '渔翁'],
      places: [],
      relationships: [],
      suzhouElements: [],
      summary: '描写冰天雪地中渔翁孤傲独钓的场景。',
      coordinates: { lat: 26.435, lng: 111.467 }
    }
  }
];


type Theme = 'ink' | 'alchemist' | 'swiss' | 'paper' | 'minimal';

const THEMES: Record<Theme, ThemeConfig> = {
  ink: {
    name: '古典水墨',
    bg: 'bg-[#f5f5f0]',
    sidebar: 'bg-white/40',
    card: 'bg-white',
    text: 'text-[#1a1a1a]',
    accent: 'bg-[#5A5A40]',
    accentText: 'text-[#5A5A40]',
    border: 'border-[#d1d1ca]',
    font: 'font-serif-zh'
  },
  alchemist: {
    name: '玄青炼金',
    bg: 'bg-[#0a0c14]',
    sidebar: 'bg-[#121624]/80',
    card: 'bg-[#1a1f33]',
    text: 'text-[#d4d9e6]',
    accent: 'bg-[#c5a86d]',
    accentText: 'text-[#c5a86d]',
    border: 'border-[#2d3550]',
    font: 'font-serif-zh'
  },
  swiss: {
    name: '包豪斯格',
    bg: 'bg-[#ffffff]',
    sidebar: 'bg-[#f0f0f0]',
    card: 'bg-white',
    text: 'text-[#000000]',
    accent: 'bg-[#ff3b30]',
    accentText: 'text-[#ff3b30]',
    border: 'border-black',
    font: 'font-sans'
  },
  paper: {
    name: '古籍纸本',
    bg: 'bg-[#e8dec0]',
    sidebar: 'bg-[#d8ccaf]/40',
    card: 'bg-[#f4ebd0]',
    text: 'text-[#3d2b1f]',
    accent: 'bg-[#8b4513]',
    accentText: 'text-[#8b4513]',
    border: 'border-[#b8a98f]',
    font: 'font-serif-zh'
  },
  minimal: {
    name: '极简白',
    bg: 'bg-[#fafafa]',
    sidebar: 'bg-[#ffffff]',
    card: 'bg-white',
    text: 'text-[#404040]',
    accent: 'bg-[#171717]',
    accentText: 'text-[#171717]',
    border: 'border-[#eaeaea]',
    font: 'font-sans'
  }
};

export default function App() {
  const [activeTab, setActiveTab] = useState<'home' | 'search' | 'imagery' | 'hubs' | 'relations' | 'suzhou' | 'ingest'>('home');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPoem, setSelectedPoem] = useState<Poem | null>(null);
  const [currentTheme, setCurrentTheme] = useState<Theme>('ink');
  const [selectedHub, setSelectedHub] = useState<SpatialHub | null>(null);

  const theme = THEMES[currentTheme];

  const filteredPoems = useMemo(() => {
    if (!searchQuery.trim()) return SAMPLE_POEMS;
    const q = searchQuery.toLowerCase();
    return SAMPLE_POEMS.filter(p => 
      p.title.toLowerCase().includes(q) || 
      p.author.toLowerCase().includes(q) || 
      p.content.toLowerCase().includes(q) ||
      p.metadata?.imagery.some(img => img.toLowerCase().includes(q)) ||
      p.metadata?.suzhouElements.some(el => el.toLowerCase().includes(q))
    );
  }, [searchQuery]);

  return (
    <div className={cn("flex h-screen transition-all duration-1000 overflow-hidden selection:bg-current selection:text-white", theme.bg, theme.text, theme.font)}>
      {/* Decorative Background Elements */}
      {currentTheme === 'alchemist' && (
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-[#c5a86d] opacity-[0.03] blur-[120px]" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-[#4f5b93] opacity-[0.05] blur-[150px]" />
        </div>
      )}
      {currentTheme === 'paper' && (
        <div className="absolute inset-0 opacity-[0.15] mix-blend-multiply pointer-events-none" style={{ backgroundImage: 'radial-gradient(#3d2b1f 0.5px, transparent 0.5px)', backgroundSize: '10px 10px' }} />
      )}
      
      {/* Sidebar */}
      <nav className={cn("w-72 border-r flex flex-col p-8 space-y-10 backdrop-blur-xl z-10 transition-all duration-700", theme.sidebar, theme.border)}>
        <div className="flex items-center space-x-2">
          <div className={cn("w-10 h-10 rounded-full flex items-center justify-center text-white transition-colors", theme.accent)}>
            <BookOpen size={20} />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight">全唐诗</h1>
            <p className="text-[10px] uppercase tracking-widest opacity-50 font-serif-en italic">Tang Verse Explorer</p>
          </div>
        </div>

        <div className="flex-1 space-y-1">
          <NavItem theme={theme} icon={Sparkles} label="首页推荐" active={activeTab === 'home'} onClick={() => setActiveTab('home')} />
          <NavItem theme={theme} icon={Search} label="全文检索" active={activeTab === 'search'} onClick={() => setActiveTab('search')} />
          <NavItem theme={theme} icon={Wind} label="意象检索" active={activeTab === 'imagery'} onClick={() => setActiveTab('imagery')} />
          <NavItem theme={theme} icon={SuzhouIcon} label="空间聚类" active={activeTab === 'hubs'} onClick={() => setActiveTab('hubs')} />
          <NavItem theme={theme} icon={Users} label="人物磁场" active={activeTab === 'relations'} onClick={() => setActiveTab('relations')} />
          <NavItem theme={theme} icon={Navigation} label="苏州特辑" active={activeTab === 'suzhou'} onClick={() => setActiveTab('suzhou')} />
        </div>

        <div className={cn("pt-6 border-t", theme.border)}>
          <p className="text-[10px] uppercase tracking-widest opacity-40 mb-4 px-4">界面风格</p>
          <div className="grid grid-cols-2 gap-2 px-2">
            {(Object.keys(THEMES) as Theme[]).map((t) => (
              <button
                key={t}
                onClick={() => setCurrentTheme(t)}
                className={cn(
                  "px-3 py-2 rounded-xl border text-[10px] font-bold transition-all text-center uppercase tracking-widest",
                  currentTheme === t 
                    ? cn("border-transparent text-white shadow-md", theme.accent) 
                    : cn("bg-transparent opacity-40 hover:opacity-100", theme.border)
                )}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        <div className={cn("pt-6 mt-2 border-t", theme.border)}>
          <NavItem theme={theme} icon={Upload} label="卷宗导入" active={activeTab === 'ingest'} onClick={() => setActiveTab('ingest')} />
          <NavItem theme={theme} icon={Settings} label="索引设置" active={false} onClick={() => {}} />
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative">
        <AnimatePresence mode="wait">
          {activeTab === 'home' && (
            <motion.div 
              key="home"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="p-12 max-w-4xl mx-auto"
            >
              <header className="mb-20 text-center relative">
                <p className={cn("text-[10px] uppercase tracking-[0.5em] mb-4 opacity-70 font-mono", currentTheme === 'alchemist' && 'text-[#c5a86d]')}>Featured Classical Composition</p>
                <h2 className={cn("text-8xl font-black mb-6 tracking-tighter transition-all duration-1000", currentTheme === 'alchemist' && 'text-glow')}>枫桥夜泊</h2>
                <div className="flex items-center justify-center space-x-6 text-sm italic opacity-60">
                  <span className="font-hand text-2xl">[唐] 张继</span>
                  <span className={cn("w-px h-6", theme.accent, "opacity-20")} />
                  <span className="uppercase tracking-widest text-xs">Vol. 242</span>
                </div>
              </header>

              <div className={cn("p-16 rounded-[4rem] shadow-2xl border mb-20 relative overflow-hidden group transition-all duration-1000", theme.card, theme.border, currentTheme === 'swiss' && 'border-4')}>
                <div className={cn("absolute -top-10 -right-10 p-8 opacity-[0.02] text-[20rem] font-black pointer-events-none group-hover:opacity-[0.05] transition-all duration-1000", theme.text)}>
                  唐
                </div>
                <p className={cn("text-5xl leading-[1.3] text-center whitespace-pre-line tracking-[0.2em] italic font-medium", currentTheme === 'paper' && 'font-hand text-6xl')}>
                  月落乌啼霜满天，江枫渔火对愁眠。<br />
                  姑苏城外寒山寺，夜半钟声到客船。
                </p>
              </div>

              <div className="grid grid-cols-3 gap-6">
                <FeatureCard theme={theme} title="核心意象" items={['月', '乌', '霜', '渔火']} />
                <FeatureCard theme={theme} title="地理坐标" items={['姑苏', '枫桥', '寒山寺']} accent />
                <FeatureCard theme={theme} title="人物羁绊" items={['旅人', '张继']} />
              </div>
            </motion.div>
          )}

          {activeTab === 'search' && (
            <motion.div key="search" className="p-8 h-full flex flex-col">
              <div className="max-w-xl mx-auto w-full mb-8">
                <div className="relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 opacity-30" size={20} />
                  <input 
                    type="text"
                    placeholder="搜索标题、作者、正文或意象..."
                    className={cn(
                      "w-full border rounded-full py-4 pl-12 pr-6 focus:outline-none transition-all shadow-sm",
                      theme.card, theme.border, "focus:ring-2 focus:ring-offset-2", currentTheme === 'night' ? 'focus:ring-white/20' : 'focus:ring-black/5'
                    )}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                </div>
                <div className="flex gap-2 mt-4 overflow-x-auto pb-2 scrollbar-none">
                  {['钟声', '渔火', '夜泊', '秋江', '月', '苏州', '别离'].map(tag => (
                    <button 
                      key={tag}
                      onClick={() => setSearchQuery(tag)}
                      className={cn("px-4 py-1 rounded-full border text-xs transition-colors whitespace-nowrap", theme.card, theme.border, "hover:opacity-80")}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-5xl mx-auto w-full overflow-y-auto">
                {filteredPoems.map(poem => (
                  <div key={poem.id}>
                    <PoemCard theme={theme} poem={poem} onSelect={() => setSelectedPoem(poem)} />
                  </div>
                ))}
                {filteredPoems.length === 0 && (
                  <div className="col-span-full py-20 text-center opacity-30 italic">
                    未找到包含该意象或文字的诗歌
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {activeTab === 'imagery' && (
            <motion.div key="imagery" className="p-12 h-full overflow-y-auto">
               <header className="mb-12">
                  <h2 className="text-4xl font-bold mb-2">意象检索</h2>
                  <p className="text-sm opacity-50 font-serif-en italic">Semantic Imagery Search & Extraction</p>
               </header>

               <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
                  {['钟声', '渔火', '夜泊', '秋江', '月光', '流水', '柳', '酒'].map(img => (
                    <button 
                      key={img} 
                      onClick={() => { setSearchQuery(img); setActiveTab('search'); }}
                      className={cn("p-6 rounded-3xl border text-center transition-all hover:scale-105", theme.card, theme.border)}
                    >
                      <Hash size={16} className="mx-auto mb-2 opacity-30" />
                      <span className="font-bold text-xl">{img}</span>
                    </button>
                  ))}
               </div>

               <div className={cn("p-12 rounded-[3.5rem] border text-center", theme.card, theme.border)}>
                  <p className="opacity-50 italic">点击上方意象或在搜索框输入意象词，我们将为您检索《全唐诗》中所有关联诗篇。</p>
               </div>
            </motion.div>
          )}

          {activeTab === 'hubs' && (
            <motion.div key="hubs" className="p-8 h-full flex flex-col overflow-hidden">
               <header className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
                 <div>
                    <h2 className="text-3xl font-bold font-serif-zh">空间聚类</h2>
                    <p className="text-sm opacity-50 font-serif-en italic">Conceptual Spatial Hubs & Relationship Mapping</p>
                 </div>
                 <div className="flex gap-4">
                    <div className="text-center px-4 py-1 rounded bg-[#5A5A40]/10 border border-[#5A5A40]/20">
                      <p className="text-[10px] opacity-50 uppercase tracking-widest">活跃空间</p>
                      <p className="text-lg font-bold">1,248</p>
                    </div>
                    <div className="text-center px-4 py-1 rounded bg-[#8B0000]/10 border border-[#8B0000]/20">
                      <p className="text-[10px] opacity-50 uppercase tracking-widest">总诗量</p>
                      <p className="text-lg font-bold text-[#8B0000]">12,504</p>
                    </div>
                 </div>
               </header>

               <div className="flex-1 overflow-y-auto pr-4 space-y-8 scrollbar-custom">
                 <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                   {SPATIAL_HUBS.map(hub => (
                    <div key={hub.name} onClick={() => setSelectedHub(hub)}>
                      <SpatialHubCard hub={hub} theme={theme} />
                    </div>
                   ))}
                 </div>
               </div>

               {/* Hub Detailed Overlay */}
               <AnimatePresence>
                 {selectedHub && (
                   <motion.div 
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    className="absolute inset-0 z-40 p-8 flex items-center justify-center bg-black/20 backdrop-blur-sm"
                    onClick={() => setSelectedHub(null)}
                   >
                     <div 
                      className={cn("max-w-2xl w-full p-12 rounded-[4rem] shadow-2xl relative", theme.card)}
                      onClick={e => e.stopPropagation()}
                     >
                       <button onClick={() => setSelectedHub(null)} className="absolute top-8 right-8 p-2 hover:bg-black/5 rounded-full">
                         <ChevronRight size={24} className="rotate-90 md:rotate-0" />
                       </button>
                       
                       <h3 className="text-6xl font-bold font-serif-zh mb-4">{selectedHub.name}</h3>
                       <p className="text-lg opacity-60 mb-12">{selectedHub.description}</p>

                       <div className="grid grid-cols-2 gap-12">
                          <div className="space-y-8">
                            <div>
                              <h4 className="border-b pb-2 mb-4 font-bold text-xs uppercase tracking-widest opacity-40">相关诗歌</h4>
                              <p className="text-4xl font-serif-en"><span className="font-bold">{selectedHub.poemCount}</span> 首</p>
                            </div>
                            <div>
                               <h4 className="border-b pb-2 mb-4 font-bold text-xs uppercase tracking-widest opacity-40">相关意象</h4>
                               <div className="flex flex-wrap gap-3">
                                  {selectedHub.imagery.map(img => (
                                    <span key={img} className={cn("px-4 py-1.5 rounded-full text-sm font-bold border", theme.border)}>{img}</span>
                                  ))}
                               </div>
                            </div>
                          </div>
                          <div className="space-y-8">
                            <div>
                               <h4 className="border-b pb-2 mb-4 font-bold text-xs uppercase tracking-widest opacity-40">相关人物</h4>
                               <ul className="space-y-2">
                                  {selectedHub.people.map(p => (
                                    <li key={p} className="text-xl font-serif-zh font-medium underline underline-offset-4 decoration-current/20 hover:decoration-current transition-all cursor-pointer">{p}</li>
                                  ))}
                               </ul>
                            </div>
                            <div>
                               <h4 className="border-b pb-2 mb-4 font-bold text-xs uppercase tracking-widest opacity-40">相关空间</h4>
                               <div className="flex flex-wrap gap-4">
                                  {selectedHub.relatedSpaces.map(s => (
                                    <div key={s} className="flex items-center gap-2 text-lg font-medium opacity-70">
                                      <Link2 size={16} /> {s}
                                    </div>
                                  ))}
                               </div>
                            </div>
                          </div>
                       </div>
                     </div>
                   </motion.div>
                 )}
               </AnimatePresence>
            </motion.div>
          )}

          {activeTab === 'relations' && (
            <motion.div key="relations" className="p-12 h-full overflow-y-auto">
               <header className="mb-12 text-center md:text-left">
                  <h2 className="text-4xl font-bold mb-2">人物磁场</h2>
                  <p className="text-sm opacity-50 font-serif-en italic">The Literary Social Network of Tang Dynasty</p>
               </header>

               <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                  {[
                    { p1: '白居易', p2: '刘禹锡', type: '酬唱之交', detail: '苏州刺史任上的深度交往', intensity: 95 },
                    { p1: '李白', p2: '孟浩然', type: '师友之情', detail: '《送孟浩然之广陵》', intensity: 88 },
                    { p1: '杜甫', p2: '李白', type: '倾慕之情', detail: '《梦李白》', intensity: 92 },
                    { p1: '王维', p2: '裴迪', type: '辋川隐友', detail: '《辋川集》合著', intensity: 85 }
                  ].map((rel, i) => (
                    <div key={i}>
                      <RelationNode rel={rel} theme={theme} />
                    </div>
                  ))}
               </div>

               <div className={cn("mt-12 p-8 rounded-[3rem] border transition-all italic text-center opacity-40", theme.card, theme.border)}>
                 [ 更多人物羁绊将由 AI 在解析 900 卷卷宗时自动提取 ]
               </div>
            </motion.div>
          )}

          {activeTab === 'suzhou' && (
            <motion.div key="suzhou" className="p-12 h-full overflow-y-auto">
               <h2 className="text-4xl font-bold mb-8">苏州元素专题 <span className="text-sm font-normal opacity-50 ml-4 font-serif-en italic">The Spirit of Gusu</span></h2>
               <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
                  <div className="space-y-6">
                    <p className="text-lg leading-relaxed opacity-80">
                      苏州（古称姑苏）在《全唐诗》中占据着举足轻重的地位。从张继的枫桥到白居易的阊门，诗人们用笔尖勾勒出了这座水城的灵魂。
                    </p>
                    <div className={cn("p-8 rounded-[2.5rem] border transition-colors", theme.card, theme.border)}>
                      <h4 className="font-bold mb-4 flex items-center gap-2"><Sparkles size={18} /> 高频词云</h4>
                      <div className="flex flex-wrap gap-4">
                        {['寒山寺', '枫桥', '吴姬', '虎丘', '阊门', '太湖', '平江', '西施'].map(w => (
                          <span key={w} className="text-xl font-medium opacity-60 hover:opacity-100 cursor-default transition-all hover:scale-110">{w}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className={cn("aspect-square rounded-[3.5rem] overflow-hidden border flex items-center justify-center italic opacity-50 text-sm p-12 text-center", theme.card, theme.border)}>
                    [ 这里将展示苏州地图与诗歌分布的叠加分析 ]
                  </div>
               </div>
            </motion.div>
          )}

          {activeTab === 'ingest' && (
            <motion.div key="ingest" className="p-12 flex items-center justify-center h-full">
              <div className="max-w-lg w-full text-center">
                <div className={cn("mb-8 p-12 border-2 border-dashed rounded-[3.5rem] transition-all cursor-pointer group", theme.card, theme.border, "hover:opacity-80")}>
                  <Upload size={48} className="mx-auto mb-4 opacity-20 group-hover:scale-110 transition-transform" />
                  <h3 className="text-xl font-bold mb-2">上传全唐诗 HTML 卷宗</h3>
                  <p className="text-xs opacity-50 uppercase tracking-widest font-serif-en">Supported: .html, .htm (900 Volumes)</p>
                </div>
                <p className="text-sm opacity-60">我们会利用 Gemini AI 自动解析并建立 Meilisearch 索引。</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Poem Detail Panel */}
      <AnimatePresence>
        {selectedPoem && (
          <motion.div 
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            className={cn("absolute top-0 right-0 w-96 h-full shadow-2xl z-50 p-8 border-l overflow-y-auto transition-colors duration-500", theme.card, theme.border)}
          >
            <button onClick={() => setSelectedPoem(null)} className={cn("absolute top-4 right-4 p-2 rounded-full transition-colors", currentTheme === 'night' ? 'hover:bg-white/10' : 'hover:bg-black/5')}>
              <ChevronRight size={24} />
            </button>
            <h3 className="text-3xl font-bold mb-1">{selectedPoem.title}</h3>
            <p className="opacity-50 mb-8">{selectedPoem.author}</p>
            
            <div className={cn("p-6 rounded-2xl mb-8 leading-relaxed whitespace-pre-line tracking-widest font-medium italic transition-colors", currentTheme === 'night' ? 'bg-white/5' : 'bg-black/5')}>
              {selectedPoem.content}
            </div>

            {selectedPoem.metadata && (
              <div className="space-y-6">
                <div>
                  <h4 className="text-[10px] uppercase tracking-widest font-serif-en mb-3 opacity-40">Modern Summary</h4>
                  <p className="text-sm leading-relaxed opacity-80">{selectedPoem.metadata.summary}</p>
                </div>
                <div>
                  <h4 className="text-[10px] uppercase tracking-widest font-serif-en mb-3 opacity-40">Poetic Imagery</h4>
                  <div className="flex flex-wrap gap-2">
                    {selectedPoem.metadata.imagery.map(img => (
                      <span key={img} className={cn("px-3 py-1 rounded-lg text-[10px] font-bold uppercase tracking-wider", currentTheme === 'night' ? 'bg-white/10 text-white' : 'bg-black/5 text-black/60')}>#{img}</span>
                    ))}
                  </div>
                </div>
                {selectedPoem.metadata.suzhouElements.length > 0 && (
                  <div>
                    <h4 className={cn("text-[10px] uppercase tracking-widest font-serif-en mb-3 opacity-80", theme.accentText)}>Suzhou Identity</h4>
                    <div className="space-y-1">
                      {selectedPoem.metadata.suzhouElements.map(el => (
                        <div key={el} className="flex items-center gap-2 text-sm">
                          <span className={cn("w-1.5 h-1.5 rounded-full", theme.accent)} />
                          {el}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function NavItem({ theme, icon: Icon, label, active, onClick }: { theme: ThemeConfig, icon: any, label: string, active: boolean, onClick: () => void }) {
  return (
    <button 
      onClick={onClick}
      className={cn(
        "w-full flex items-center space-x-3 px-4 py-3 rounded-2xl transition-all duration-300 group",
        active ? cn("text-white shadow-lg", theme.accent) : "hover:bg-black/5"
      )}
    >
      <Icon size={18} className={cn(active ? "opacity-100" : "opacity-40 group-hover:opacity-70")} />
      <span className={cn("text-sm font-medium tracking-wide", active ? "opacity-100" : "opacity-70")}>{label}</span>
      {active && <motion.div layoutId="nav-pill" className="ml-auto w-1.5 h-1.5 bg-white rounded-full" />}
    </button>
  );
}

function FeatureCard({ theme, title, items, accent }: { theme: ThemeConfig, title: string, items: string[], accent?: boolean }) {
  return (
    <div className={cn(
      "p-6 rounded-[2rem] border transition-colors duration-500",
      accent ? cn("text-white border-transparent", theme.accent) : cn("border transition-colors", theme.card, theme.border)
    )}>
      <h4 className={cn("text-[10px] uppercase tracking-widest mb-4 opacity-50", accent && "text-white/70")}>{title}</h4>
      <div className="space-y-2">
        {items.slice(0, 4).map(item => (
          <div key={item} className="flex items-center space-x-2 text-sm font-medium">
            <span className={cn("w-1.5 h-1.5 rounded-full", accent ? "bg-white" : theme.accent)} />
            <span>{item}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function PoemCard({ theme, poem, onSelect }: { theme: ThemeConfig, poem: Poem, onSelect: () => void }) {
  return (
    <div 
      onClick={onSelect}
      className={cn(
        "border p-6 rounded-[2.5rem] transition-all cursor-pointer group shadow-sm hover:shadow-lg hover:-translate-y-1",
        theme.card, theme.border, "hover:border-[#5A5A40]"
      )}
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className={cn("text-2xl font-bold transition-colors", theme.accentText)}>{poem.title}</h3>
          <p className="text-xs opacity-50 mt-1">{poem.author}</p>
        </div>
        <div className="text-[10px] uppercase tracking-widest opacity-30 font-serif-en">
          Vol. {poem.volume}
        </div>
      </div>
      <p className="text-sm opacity-70 line-clamp-2 italic mb-4 leading-relaxed">
        {poem.content}
      </p>
      <div className="flex flex-wrap gap-1">
        {poem.metadata?.imagery.slice(0, 3).map(img => (
          <span key={img} className={cn("text-[9px] px-2 py-0.5 rounded-md opacity-60", theme.bg)}>#{img}</span>
        ))}
      </div>
    </div>
  );
}

function SpatialHubCard({ hub, theme }: { hub: SpatialHub, theme: ThemeConfig }) {
  return (
    <div className={cn("p-8 rounded-[3rem] border transition-all hover:shadow-xl group", theme.card, theme.border)}>
       <div className="flex justify-between items-start mb-6">
          <div>
            <h3 className="text-4xl font-bold font-serif-zh mb-2">{hub.name}</h3>
            <p className="text-sm opacity-60 max-w-xs">{hub.description}</p>
          </div>
          <div className={cn("px-4 py-2 rounded-2xl text-white font-bold flex flex-col items-center", theme.accent)}>
            <span className="text-2xl">{hub.poemCount}</span>
            <span className="text-[8px] uppercase tracking-tighter opacity-70">相关诗歌</span>
          </div>
       </div>

       <div className="grid grid-cols-2 gap-8">
          <div className="space-y-4">
             <div>
                <h4 className="flex items-center gap-2 text-[10px] uppercase tracking-widest opacity-40 mb-3"><Hash size={12} /> 相关意象</h4>
                <div className="flex flex-wrap gap-2">
                   {hub.imagery.map(img => (
                     <span key={img} className={cn("px-3 py-1 rounded-full text-xs font-medium border", theme.border, "hover:opacity-100 opacity-70 transition-opacity cursor-default")}>{img}</span>
                   ))}
                </div>
             </div>
             <div>
                <h4 className="flex items-center gap-2 text-[10px] uppercase tracking-widest opacity-40 mb-3"><Users size={12} /> 相关人物</h4>
                <div className="flex flex-wrap gap-2">
                   {hub.people.map(p => (
                     <span key={p} className="text-sm font-medium hover:underline cursor-pointer">{p}</span>
                   ))}
                </div>
             </div>
          </div>

          <div className="space-y-4">
             <div className={cn("p-6 rounded-[2rem] border transition-colors", theme.bg, theme.border)}>
                <h4 className="flex items-center gap-2 text-[10px] uppercase tracking-widest opacity-40 mb-4 text-inherit"><Link2 size={12} /> 关联空间</h4>
                <div className="space-y-3">
                   {hub.relatedSpaces.map(space => (
                     <div key={space} className="flex items-center justify-between group/item cursor-pointer">
                        <span className="text-sm font-medium opacity-70 group-hover/item:opacity-100 transition-opacity">{space}</span>
                        <ArrowUpRight size={14} className="opacity-0 group-hover/item:opacity-100 transition-all -translate-x-1 group-hover/item:translate-x-0" />
                     </div>
                   ))}
                </div>
             </div>
          </div>
       </div>
    </div>
  );
}

function RelationNode({ rel, theme }: { rel: any, theme: ThemeConfig }) {
  return (
    <div className={cn("p-6 rounded-[2rem] border relative overflow-hidden group hover:scale-[1.02] transition-all", theme.card, theme.border)}>
       <div className="flex items-center justify-between mb-6">
          <div className="flex -space-x-3">
             <div className={cn("w-12 h-12 rounded-full border-2 border-white flex items-center justify-center font-bold text-white", theme.accent)}>{rel.p1[0]}</div>
             <div className={cn("w-12 h-12 rounded-full border-2 border-white flex items-center justify-center font-bold text-white opacity-80", theme.accent)}>{rel.p2[0]}</div>
          </div>
          <div className="text-right">
             <p className="text-[10px] uppercase tracking-widest opacity-30 mb-1">关系强度</p>
             <p className="font-bold font-serif-en">{rel.intensity}%</p>
          </div>
       </div>
       <h4 className="text-lg font-bold mb-1">{rel.p1} & {rel.p2}</h4>
       <p className={cn("text-xs font-serif-zh font-bold mb-4 uppercase tracking-[0.2em]", theme.accentText)}>{rel.type}</p>
       <p className="text-xs opacity-60 leading-relaxed italic">{rel.detail}</p>
       
       <div className="absolute bottom-0 left-0 h-1 bg-current opacity-10" style={{ width: `${rel.intensity}%` }} />
    </div>
  );
}
