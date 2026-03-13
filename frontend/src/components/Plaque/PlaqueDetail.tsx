import { useParams, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { usePlaque } from '../../hooks/usePlaques';
import Lightbox from '../Gallery/Lightbox';

export default function PlaqueDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data: plaque, isLoading, error } = usePlaque(Number(id));
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [lightboxIndex, setLightboxIndex] = useState(0);

  const openLightbox = (index: number) => {
    setLightboxIndex(index);
    setLightboxOpen(true);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading plaque details...</p>
        </div>
      </div>
    );
  }

  if (error || !plaque) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h1 className="text-2xl font-bold text-gray-800 mb-4">Plaque not found</h1>
        <button onClick={() => navigate('/')} className="text-blue-600 hover:underline">
          ← Back to map
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <button onClick={() => navigate('/')} className="text-blue-600 hover:underline mb-6 flex items-center">
          <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back to map
        </button>

        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          {plaque.images.length > 0 && (
            <img 
              src={plaque.images[0].url} 
              alt={plaque.title}
              className="w-full h-96 object-cover cursor-pointer hover:opacity-95 transition"
              onClick={() => openLightbox(0)}
            />
          )}

          <div className="p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">{plaque.title}</h1>

            {plaque.address && (
              <div className="flex items-start mb-4 text-gray-600">
                <svg className="w-5 h-5 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>{plaque.address}</span>
              </div>
            )}

            {plaque.categories.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-6">
                {plaque.categories.map(cat => (
                  <span key={cat.id} className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                    {cat.name}
                  </span>
                ))}
              </div>
            )}

            {plaque.description && (
              <div className="prose max-w-none mb-6">
                <h2 className="text-xl font-semibold mb-2">Description</h2>
                <p className="text-gray-700 whitespace-pre-wrap">{plaque.description}</p>
              </div>
            )}

            {plaque.inscription && (
              <div className="bg-gray-50 p-4 rounded-lg mb-6">
                <h2 className="text-xl font-semibold mb-2">Inscription</h2>
                <p className="text-gray-700 italic whitespace-pre-wrap">{plaque.inscription}</p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-6">
              {plaque.year_erected && (
                <div>
                  <span className="font-semibold">Year Erected:</span> {plaque.year_erected}
                </div>
              )}
              {plaque.organization && (
                <div>
                  <span className="font-semibold">Organization:</span> {plaque.organization}
                </div>
              )}
            </div>

            {plaque.source_url && (
              <a
                href={plaque.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center text-blue-600 hover:underline mb-6"
              >
                View on Heritage Portal
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            )}

            {plaque.images.length > 1 && (
              <div>
                <h2 className="text-xl font-semibold mb-4">Gallery ({plaque.images.length} images)</h2>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {plaque.images.map((img, idx) => (
                    <img
                      key={img.id}
                      src={img.url}
                      alt={img.caption || plaque.title}
                      className="w-full h-48 object-cover rounded-lg cursor-pointer hover:opacity-90 transition"
                      onClick={() => openLightbox(idx)}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {lightboxOpen && (
        <Lightbox
          images={plaque.images}
          initialIndex={lightboxIndex}
          onClose={() => setLightboxOpen(false)}
        />
      )}
    </div>
  );
}
