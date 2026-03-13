import { useState } from 'react';
import type { Image } from '../../types/plaque';

interface LightboxProps {
  images: Image[];
  initialIndex?: number;
  onClose: () => void;
}

export default function Lightbox({ images, initialIndex = 0, onClose }: LightboxProps) {
  const [currentIndex, setCurrentIndex] = useState(initialIndex);

  const goNext = () => setCurrentIndex((i) => (i + 1) % images.length);
  const goPrev = () => setCurrentIndex((i) => (i - 1 + images.length) % images.length);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') onClose();
    if (e.key === 'ArrowRight') goNext();
    if (e.key === 'ArrowLeft') goPrev();
  };

  return (
    <div
      className="fixed inset-0 z-[9999] bg-black bg-opacity-90 flex items-center justify-center"
      onClick={onClose}
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      <button
        onClick={onClose}
        className="absolute top-4 right-4 text-white hover:text-gray-300 text-4xl"
      >
        ×
      </button>

      {images.length > 1 && (
        <>
          <button
            onClick={(e) => { e.stopPropagation(); goPrev(); }}
            className="absolute left-4 text-white hover:text-gray-300 text-4xl"
          >
            ‹
          </button>
          <button
            onClick={(e) => { e.stopPropagation(); goNext(); }}
            className="absolute right-4 text-white hover:text-gray-300 text-4xl"
          >
            ›
          </button>
        </>
      )}

      <div className="max-w-5xl max-h-[90vh] px-16" onClick={(e) => e.stopPropagation()}>
        <img
          src={images[currentIndex].url}
          alt={images[currentIndex].caption || ''}
          className="max-w-full max-h-[80vh] object-contain"
        />
        {images[currentIndex].caption && (
          <p className="text-white text-center mt-4">{images[currentIndex].caption}</p>
        )}
        {images.length > 1 && (
          <p className="text-white text-center mt-2 text-sm">
            {currentIndex + 1} / {images.length}
          </p>
        )}
      </div>
    </div>
  );
}
