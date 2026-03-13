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
        className="absolute top-4 right-4 z-[1000] bg-white rounded-lg shadow-lg p-3 hover:bg-gray-50"
        aria-label="Toggle filters"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      
      {isOpen && (
        <div className="absolute top-4 right-4 z-[1000] w-64 bg-white rounded-lg shadow-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-bold text-lg">Filter by Category</h3>
            <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-gray-600">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div className="space-y-2 max-h-96 overflow-y-auto mb-3">
            {categories?.map((category) => (
              <label key={category.id} className="flex items-center justify-between cursor-pointer hover:bg-gray-50 p-1 rounded">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={selectedCategories.includes(category.id)}
                    onChange={() => onCategoryToggle(category.id)}
                    className="rounded text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm">{category.name}</span>
                </div>
                <span className="text-xs text-gray-500">({category.plaque_count})</span>
              </label>
            ))}
          </div>
          <div className="flex gap-2">
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
