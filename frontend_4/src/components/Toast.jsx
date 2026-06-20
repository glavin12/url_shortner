import { createContext, useContext, useState, useCallback, useMemo } from 'react';

const ToastContext = createContext(null);

let toastId = 0;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((message, type = 'info') => {
    const id = ++toastId;
    setToasts((prev) => [...prev, { id, message, type }]);

    setTimeout(() => {
      setToasts((prev) =>
        prev.map((t) => (t.id === id ? { ...t, exiting: true } : t))
      );
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 300);
    }, 3500);
  }, []);

  const toast = useMemo(
    () => ({
      success: (msg) => addToast(msg, 'success'),
      error: (msg) => addToast(msg, 'error'),
      info: (msg) => addToast(msg, 'info'),
    }),
    [addToast]
  );

  return (
    <ToastContext.Provider value={toast}>
      {children}
      <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3">
        {toasts.map((t) => {
          const baseClasses = "min-w-[300px] px-6 py-4 rounded-xl shadow-2xl font-medium text-sm transition-all duration-300 transform border";
          const exitClasses = t.exiting ? "opacity-0 translate-x-8" : "opacity-100 translate-x-0";
          
          let typeClasses = "";
          if (t.type === 'success') {
            typeClasses = "bg-green-500/10 text-green-400 border-green-500/20";
          } else if (t.type === 'error') {
            typeClasses = "bg-red-500/10 text-red-400 border-red-500/20";
          } else {
            typeClasses = "bg-[#222222] text-cream border-white/10";
          }

          return (
            <div key={t.id} className={`${baseClasses} ${exitClasses} ${typeClasses}`}>
              {t.message}
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}
