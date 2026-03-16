import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../../services/api';
import type { Category } from '../../types/plaque';

interface CategoryWithCount extends Category {
  plaque_count: number;
}

interface FilterPanelProps {
  selectedCategories: number[];
  onCategoryToggle: (categoryId: number) => void;
  onClearAll?: () => void;
  onSelectAll?: () => void;
}

export default function FilterPanel({ selectedCategories, onCategoryToggle, onClearAll, onSelectAll }: FilterPanelProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { data: categories, isLoading } = useQuery({
    queryKey: ['categories'],
    queryFn: () => api.get<CategoryWithCount[]>('/categories').then(res => res.data),
  });

  if (isLoading) return null;

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="absolute top-4 right-4 z-[1000] bg-white rounded-lg shadow-lg p-3 hover:bg-gray-50 text-xl leading-none"
        aria-label="Toggle filters"
      >
        ☰
      </button>
      
      {isOpen && (
        <div className="absolute top-4 right-4 z-[1000] w-64 bg-white rounded-lg shadow-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-bold text-lg">Filter by Category</h3>
            <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-gray-600" aria-label="Close filters">
              ✕
            </button>
          </div>
          <div className="mb-3" style={{ maxHeight: '24rem', overflowY: 'auto', WebkitOverflowScrolling: 'touch' }}>
            {categories?.map((category) => (
              <div
                key={category.id}
                onClick={() => onCategoryToggle(category.id)}
                className="flex items-center justify-between p-2 rounded cursor-pointer hover:bg-gray-50 active:bg-gray-100"
              >
                <div className="flex items-center gap-2">
                  <span className="inline-flex items-center justify-center w-5 h-5 border-2 rounded text-xs" style={{
                    borderColor: selectedCategories.includes(category.id) ? '#2563eb' : '#d1d5db',
                    backgroundColor: selectedCategories.includes(category.id) ? '#2563eb' : 'transparent',
                    color: selectedCategories.includes(category.id) ? 'white' : 'transparent',
                  }}>
                    {selectedCategories.includes(category.id) ? '✓' : ''}
                  </span>
                  <span className="text-sm">{category.name}</span>
                </div>
                <span className="text-xs text-gray-500">({category.plaque_count})</span>
              </div>
            ))}
          </div>
          <div className="flex gap-2 border-t pt-2">
            <button
              onClick={onSelectAll}
              className="flex-1 text-sm text-blue-600 hover:text-blue-800 py-1"
            >
              Select all
            </button>
            <button
              onClick={onClearAll}
              className="flex-1 text-sm text-blue-600 hover:text-blue-800 py-1"
            >
              Clear all
            </button>
          </div>
        </div>
      )}
    </>
  );
}
