import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, Heart, PlaySquare, User, Send, Lock, ChevronRight, Star, MapPin, CheckCircle2, ThumbsUp } from 'lucide-react';

// --- MOCK DATA ---
const MOCK_MATCHES = [
  {
    id: 1,
    name: 'Aisha',
    age: 26,
    profession: 'Product Designer',
    image: 'https://placehold.co/400x500/8b5cf6/ffffff?text=Aisha',
    overallScore: 94,
    metrics: { financial: 92, nightlife: 88, goals: 96 },
    locked: false,
  },
  {
    id: 2,
    name: 'Kwame',
    age: 29,
    profession: 'Fintech Founder',
    image: 'https://placehold.co/400x500/ec4899/ffffff?text=Kwame',
    overallScore: 89,
    metrics: { financial: 95, nightlife: 75, goals: 90 },
    locked: false,
  },
  {
    id: 3,
    name: 'Wanjiku',
    age: 27,
    profession: 'Corporate Lawyer',
    image: 'https://placehold.co/400x500/10b981/ffffff?text=Wanjiku',
    overallScore: 82,
    metrics: { financial: 80, nightlife: 85, goals: 81 },
    locked: true, // Premium teased
  }
];

const MOCK_STORIES = [
  {
    id: 1,
    couple: 'Aisha & John',
    location: 'The Alchemist, Nairobi',
    votes: 1240,
    image: 'https://placehold.co/400x600/3b82f6/ffffff?text=Date+Night',
    isTop: true,
  },
  {
    id: 2,
    couple: 'Joy & Brian',
    location: 'Milan Signature',
    votes: 890,
    image: 'https://placehold.co/400x600/f59e0b/ffffff?text=Sushi+Date',
    isTop: false,
  }
];

export default function KutanaApp() {
  const [activeTab, setActiveTab] = useState('profiler');
  
  return (
    <div className="flex justify-center items-center min-h-screen bg-black p-4 font-sans">
      {/* Mobile Device Simulator Container */}
      <div className="w-full max-w-[400px] h-[800px] bg-gray-950 rounded-[40px] shadow-2xl border-8 border-gray-900 relative overflow-hidden flex flex-col">
        
        {/* Dynamic Header based on active tab */}
        <header className="px-6 pt-12 pb-4 bg-gray-950 border-b border-gray-800 z-10 flex justify-between items-center shrink-0">
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
              {activeTab === 'profiler' && 'Kutana AI'}
              {activeTab === 'matches' && 'Leaderboard'}
              {activeTab === 'stories' && 'Dream Dates'}
              {activeTab === 'profile' && 'My Profile'}
            </h1>
            <p className="text-xs text-gray-400">
              {activeTab === 'profiler' && 'Secure AI Onboarding'}
              {activeTab === 'matches' && 'Your Compatibility Matrix'}
              {activeTab === 'stories' && 'Vote for top couples'}
              {activeTab === 'profile' && 'Manage your data'}
            </p>
          </div>
          {activeTab === 'matches' && (
            <div className="bg-gradient-to-r from-yellow-400 to-yellow-600 p-2 rounded-full">
              <Star size={16} className="text-black" />
            </div>
          )}
        </header>

        {/* Main Scrollable Content Area */}
        <main className="flex-1 overflow-y-auto bg-gray-950 hide-scrollbar relative">
          {activeTab === 'profiler' && <ProfilerTab />}
          {activeTab === 'matches' && <MatchesTab />}
          {activeTab === 'stories' && <StoriesTab />}
          {activeTab === 'profile' && <ProfileTab />}
        </main>

        {/* Bottom Navigation */}
        <nav className="shrink-0 bg-gray-900 border-t border-gray-800 px-6 py-4 flex justify-between items-center rounded-b-[32px]">
          <NavItem icon={<Sparkles size={24}/>} label="AI" isActive={activeTab === 'profiler'} onClick={() => setActiveTab('profiler')} />
          <NavItem icon={<Heart size={24}/>} label="Matches" isActive={activeTab === 'matches'} onClick={() => setActiveTab('matches')} />
          <NavItem icon={<PlaySquare size={24}/>} label="Stories" isActive={activeTab === 'stories'} onClick={() => setActiveTab('stories')} />
          <NavItem icon={<User size={24}/>} label="Profile" isActive={activeTab === 'profile'} onClick={() => setActiveTab('profile')} />
        </nav>
      </div>
    </div>
  );
}

// --- SUBCOMPONENTS ---

function ProfilerTab() {
  const [messages, setMessages] = useState([
    { role: 'ai', text: 'Hey there. I am the Kutana Profiler. I use our chats to build your private compatibility matrix. To keep it focused, we only have 10 messages. Ready?' },
    { role: 'user', text: 'Yes, let\'s do this.' },
    { role: 'ai', text: 'Great. Let\'s skip the small talk. Describe your ideal Friday night in Nairobi.' }
  ]);
  const [inputText, setInputText] = useState('');
  const maxMessages = 10;
  const userMessageCount = messages.filter(m => m.role === 'user').length;
  const messagesEndRef = useRef(null);

  const handleSend = () => {
    if (!inputText.trim() || userMessageCount >= maxMessages) return;
    
    const newMsg = { role: 'user', text: inputText };
    setMessages(prev => [...prev, newMsg]);
    setInputText('');
    
    // Simulate AI response
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        role: 'ai', 
        text: 'Interesting vibe. Next question: What are your expectations regarding financial dynamics in a relationship? (e.g., 50/50, provided for, etc.)' 
      }]);
    }, 1000);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-col h-full">
      {/* Token Progress Bar */}
      <div className="px-4 py-2 bg-gray-900 sticky top-0 z-10 text-xs flex justify-between items-center">
        <span className="text-gray-400">Profiling Progress</span>
        <span className="text-purple-400 font-mono">{userMessageCount} / {maxMessages} Tokens Used</span>
      </div>
      <div className="w-full bg-gray-800 h-1">
        <div 
          className="bg-purple-500 h-1 transition-all duration-300" 
          style={{ width: `${(userMessageCount / maxMessages) * 100}%` }}
        />
      </div>

      {/* Chat History */}
      <div className="flex-1 p-4 overflow-y-auto flex flex-col space-y-4">
        <div className="text-center p-3 bg-gray-900/50 rounded-lg border border-gray-800 mb-2">
          <Lock size={14} className="inline mr-2 text-gray-400" />
          <span className="text-xs text-gray-400">Chats are vectorized and instantly deleted to comply with ODPC standards.</span>
        </div>
        
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] rounded-2xl p-3 text-sm ${
              msg.role === 'user' 
                ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-tr-none' 
                : 'bg-gray-800 text-gray-100 rounded-tl-none border border-gray-700'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Chat Input */}
      <div className="p-4 bg-gray-900 shrink-0">
        <div className="flex items-center space-x-2 bg-gray-800 rounded-full px-4 py-2 border border-gray-700 focus-within:border-purple-500 transition-colors">
          <input 
            type="text" 
            placeholder={userMessageCount >= maxMessages ? "Session complete." : "Type your honest answer..."}
            className="flex-1 bg-transparent border-none outline-none text-white text-sm"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={userMessageCount >= maxMessages}
          />
          <button 
            onClick={handleSend}
            disabled={userMessageCount >= maxMessages || !inputText.trim()}
            className="p-2 bg-purple-600 rounded-full text-white disabled:opacity-50 hover:bg-purple-500 transition-colors"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}

function MatchesTab() {
  return (
    <div className="p-4 space-y-6">
      <div className="bg-gradient-to-r from-gray-900 to-gray-800 rounded-xl p-4 border border-yellow-500/20 shadow-[0_0_15px_rgba(234,179,8,0.1)]">
        <div className="flex justify-between items-center mb-2">
          <h2 className="text-yellow-500 font-bold text-sm">Kutana Black Active</h2>
          <Star size={16} className="text-yellow-500 fill-yellow-500" />
        </div>
        <p className="text-xs text-gray-400">Leaderboard unlocked. These matches are algorithmically verified based on your AI vector profile.</p>
      </div>

      <div className="space-y-4">
        {MOCK_MATCHES.map(match => (
          <div key={match.id} className="bg-gray-900 rounded-2xl overflow-hidden border border-gray-800 relative">
            {match.locked && (
              <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-10 flex flex-col items-center justify-center p-6 text-center">
                <Lock size={32} className="text-yellow-500 mb-3" />
                <h3 className="text-white font-bold mb-1">Hidden Match</h3>
                <p className="text-xs text-gray-300">Upgrade to view the rest of your compatibility matrix.</p>
                <button className="mt-4 px-6 py-2 bg-gradient-to-r from-yellow-500 to-yellow-600 rounded-full text-black font-bold text-sm">
                  Upgrade
                </button>
              </div>
            )}
            
            <div className="flex h-32">
              <img src={match.image} alt={match.name} className="w-1/3 object-cover" />
              <div className="w-2/3 p-4 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-bold text-white text-lg flex items-center">
                        {match.name}, {match.age}
                        <CheckCircle2 size={14} className="text-blue-400 ml-1" />
                      </h3>
                      <p className="text-xs text-gray-400">{match.profession}</p>
                    </div>
                    <div className="bg-purple-900/50 border border-purple-500/30 px-2 py-1 rounded text-purple-400 font-mono font-bold text-sm">
                      {match.overallScore}%
                    </div>
                  </div>
                </div>
                
                {/* Granular Stats */}
                <div className="grid grid-cols-3 gap-2 mt-2">
                  <div className="bg-gray-800 rounded p-1.5 text-center">
                    <div className="text-[10px] text-gray-400">Financial</div>
                    <div className="text-xs text-green-400 font-bold">{match.metrics.financial}%</div>
                  </div>
                  <div className="bg-gray-800 rounded p-1.5 text-center">
                    <div className="text-[10px] text-gray-400">Nightlife</div>
                    <div className="text-xs text-pink-400 font-bold">{match.metrics.nightlife}%</div>
                  </div>
                  <div className="bg-gray-800 rounded p-1.5 text-center">
                    <div className="text-[10px] text-gray-400">Goals</div>
                    <div className="text-xs text-blue-400 font-bold">{match.metrics.goals}%</div>
                  </div>
                </div>
              </div>
            </div>
            {/* Actions */}
            <div className="bg-gray-800/50 p-2 flex justify-end space-x-2">
              <button className="p-2 rounded-full bg-gray-800 hover:bg-gray-700 text-gray-400">
                <ChevronRight size={18} className="rotate-180" />
              </button>
              <button className="p-2 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/30">
                <Heart size={18} className="fill-white" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function StoriesTab() {
  return (
    <div className="h-full flex flex-col">
      <div className="p-4 bg-gradient-to-b from-purple-900/40 to-transparent">
        <h2 className="text-xl font-bold text-white flex items-center">
          Dream Dates <Sparkles size={18} className="ml-2 text-yellow-400" />
        </h2>
        <p className="text-xs text-gray-300 mt-1">Vote for your favorite Kutana couples. Top voted wins a sponsored date at Milan.</p>
      </div>

      <div className="flex-1 p-4 overflow-y-auto space-y-6 pb-8">
        {MOCK_STORIES.map(story => (
          <div key={story.id} className="relative rounded-2xl overflow-hidden border border-gray-800 shadow-xl group">
            {story.isTop && (
              <div className="absolute top-3 left-3 z-20 bg-yellow-500 text-black text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-wide flex items-center">
                <Star size={10} className="mr-1 fill-black" /> Leading
              </div>
            )}
            
            {/* Story Image */}
            <div className="h-[300px] w-full relative">
              <img src={story.image} alt={story.couple} className="w-full h-full object-cover" />
              <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent" />
            </div>

            {/* Story Content Overlay */}
            <div className="absolute bottom-0 left-0 right-0 p-4 z-10">
              <h3 className="font-bold text-white text-xl">{story.couple}</h3>
              <div className="flex items-center text-gray-300 text-xs mt-1 mb-4">
                <MapPin size={12} className="mr-1" /> {story.location}
              </div>
              
              <div className="flex justify-between items-center">
                <div className="text-sm font-mono font-bold text-pink-400">
                  {story.votes.toLocaleString()} Votes
                </div>
                <button className="flex items-center space-x-2 bg-white text-black px-4 py-2 rounded-full text-sm font-bold hover:bg-gray-200 transition-colors">
                  <ThumbsUp size={16} />
                  <span>Vote</span>
                </button>
              </div>
            </div>
            
            {/* Progress Bar (Visual Story indicator) */}
            <div className="absolute top-2 left-2 right-2 flex space-x-1 z-10">
               <div className="h-1 bg-white/80 rounded-full flex-1" />
               <div className="h-1 bg-white/30 rounded-full flex-1" />
               <div className="h-1 bg-white/30 rounded-full flex-1" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ProfileTab() {
  return (
    <div className="p-6 h-full flex flex-col items-center pt-12">
      <div className="relative mb-4">
        <img src="https://placehold.co/200x200/333/fff?text=Me" alt="Profile" className="w-24 h-24 rounded-full border-4 border-gray-800 object-cover" />
        <div className="absolute bottom-0 right-0 bg-green-500 w-5 h-5 rounded-full border-2 border-gray-950"></div>
      </div>
      <h2 className="text-2xl font-bold text-white">David, 28</h2>
      <p className="text-gray-400 text-sm mb-8">Nairobi, Kenya</p>

      <div className="w-full space-y-3">
        <div className="bg-gray-900 p-4 rounded-xl border border-gray-800 flex justify-between items-center">
          <span className="text-sm text-gray-300">Privacy & ODPC Status</span>
          <span className="text-xs bg-green-900/50 text-green-400 px-2 py-1 rounded">Compliant</span>
        </div>
        <div className="bg-gray-900 p-4 rounded-xl border border-gray-800 flex justify-between items-center">
          <span className="text-sm text-gray-300">Subscription</span>
          <span className="text-xs font-bold text-yellow-500">Kutana Black</span>
        </div>
        <div className="bg-gray-900 p-4 rounded-xl border border-gray-800 flex justify-between items-center cursor-pointer hover:bg-gray-800 transition-colors">
          <span className="text-sm text-gray-300">Retake AI Profiling</span>
          <ChevronRight size={16} className="text-gray-500" />
        </div>
      </div>
    </div>
  );
}

function NavItem({ icon, label, isActive, onClick }) {
  return (
    <button 
      onClick={onClick}
      className={`flex flex-col items-center p-2 transition-all duration-300 ${
        isActive ? 'text-purple-400 -translate-y-1' : 'text-gray-500 hover:text-gray-300'
      }`}
    >
      <div className={`mb-1 transition-transform ${isActive ? 'scale-110' : ''}`}>
        {icon}
      </div>
      <span className="text-[10px] font-medium">{label}</span>
      {isActive && (
        <span className="absolute -bottom-1 w-1 h-1 bg-purple-400 rounded-full" />
      )}
    </button>
  );
}