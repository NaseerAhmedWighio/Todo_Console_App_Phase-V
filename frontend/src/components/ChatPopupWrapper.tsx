'use client';

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import PopupChatInterface from './PopupChatInterface';
import Robot from '../../public/robot.png'
import Image from 'next/image';

const ChatPopupWrapper = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const pathname = usePathname();

  // Prevent hydration mismatch
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Close chat when pressing Escape
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isChatOpen) {
        setIsChatOpen(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isChatOpen]);

  // Only show chat on dashboard page and after mounting
  if (!isMounted || pathname !== '/dashboard') {
    return null;
  }

  return (
    <>
      {/* Floating Chat Button */}
      {!isChatOpen && (
        <button
          className="chat-open-button88 p-2 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 glow-effect"
          onClick={() => setIsChatOpen(true)}
          aria-label="Open AI Chat Assistant"
        >
          <Image src={Robot} alt="AI Chat Assistant" width={200} height={90} className='h-12 w-20' />
        </button>
      )}

      {/* Popup Chat Interface */}
      <PopupChatInterface
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
      />
    </>
  );
};

export default ChatPopupWrapper;