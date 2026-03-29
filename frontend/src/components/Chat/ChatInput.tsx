import type { FC, KeyboardEvent } from 'react';
import { useState, useRef, useEffect } from 'react';
import { Send, Image, Mic } from 'lucide-react';
import { transcribeAPI } from '../../services/api';

interface ChatInputProps {
  onSend: (message: string, image?: File) => void;
  disabled?: boolean;
}

export const ChatInput: FC<ChatInputProps> = ({ onSend, disabled }) => {
  const [input, setInput] = useState('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    if (!disabled && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if ((input.trim() || selectedImage) && !disabled) {
      onSend(input.trim(), selectedImage || undefined);
      setInput('');
      setSelectedImage(null);
      setTimeout(() => textareaRef.current?.focus(), 0);
    }
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
    }
  };

  const handleVoiceRecord = async () => {
    if (isRecording && recorderRef.current) {
      recorderRef.current.stop();
      setIsRecording(false);
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunksRef.current = [];
      const recorder = new MediaRecorder(stream);

      recorder.ondataavailable = (e) => chunksRef.current.push(e.data);
      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach(t => t.stop());

        try {
          const res = await transcribeAPI.transcribe(blob);
          const text = res.data.text || '';
          if (text) setInput(prev => prev ? `${prev} ${text}` : text);
        } catch (err) {
          alert('语音转文字失败，请重试');
        }
      };

      recorderRef.current = recorder;
      recorder.start();
      setIsRecording(true);
    } catch (err) {
      alert('无法访问麦克风，请检查权限');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="border-t border-gray-200 dark:border-border-dark bg-white dark:bg-surface-dark p-4">
      {selectedImage && (
        <div className="mb-2 flex items-center gap-2">
          <div className="relative">
            <img src={URL.createObjectURL(selectedImage)} alt="preview" className="w-16 h-16 object-cover rounded-lg border border-border dark:border-border-dark" />
            <button type="button" onClick={() => setSelectedImage(null)} className="absolute -top-1.5 -right-1.5 w-5 h-5 bg-error text-white rounded-full text-xs flex items-center justify-center">&times;</button>
          </div>
          <span className="text-xs text-text-secondary truncate max-w-[200px]">{selectedImage.name}</span>
        </div>
      )}
      <div className="flex gap-2 items-end">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleImageSelect}
        />
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className="p-2.5 rounded-full text-text-secondary hover:text-primary hover:bg-primary-light dark:hover:bg-primary/10 disabled:opacity-40 disabled:cursor-not-allowed transition-all flex-shrink-0"
          title="上传图片"
        >
          <Image size={18} />
        </button>
        <button
          type="button"
          onClick={handleVoiceRecord}
          disabled={disabled}
          className={`p-2.5 rounded-full transition-all flex-shrink-0 ${isRecording ? 'bg-error text-white animate-pulse' : 'text-text-secondary hover:text-primary hover:bg-primary-light dark:hover:bg-primary/10'} disabled:opacity-40 disabled:cursor-not-allowed`}
          title={isRecording ? '停止录音' : '语音输入'}
        >
          <Mic size={18} />
        </button>
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={disabled ? "连接中..." : isRecording ? "录音中..." : "输入消息... (Enter发送，Shift+Enter换行)"}
          disabled={disabled}
          rows={1}
          className="flex-1 px-4 py-2.5 border border-gray-300 dark:border-border-dark rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary disabled:bg-gray-100 dark:disabled:bg-surface-dark disabled:cursor-not-allowed resize-none max-h-32 bg-white dark:bg-surface-dark text-text-primary dark:text-text-primary-dark transition-all"
          style={{ minHeight: '42px' }}
        />
        <button
          type="submit"
          disabled={disabled || (!input.trim() && !selectedImage)}
          className="bg-primary text-white p-2.5 rounded-full hover:bg-primary-hover active:scale-95 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-primary transition-all duration-200 shadow-low hover:shadow-mid flex-shrink-0"
        >
          <Send size={18} />
        </button>
      </div>
    </form>
  );
};
