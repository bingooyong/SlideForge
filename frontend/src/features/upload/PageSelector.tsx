import { useMemo } from "react";

export interface PageThumbnail {
  pageIndex: number;
  imageUrl: string;
}

export interface PageSelectorProps {
  pages: PageThumbnail[];
  selectedPages: number[];
  onChangeSelectedPages: (pages: number[]) => void;
}

export function PageSelector({ pages, selectedPages, onChangeSelectedPages }: PageSelectorProps) {
  const allSelected = useMemo(
    () => pages.length > 0 && selectedPages.length === pages.length,
    [pages.length, selectedPages.length],
  );

  const togglePage = (pageIndex: number) => {
    if (selectedPages.includes(pageIndex)) {
      onChangeSelectedPages(selectedPages.filter((p) => p !== pageIndex));
    } else {
      onChangeSelectedPages([...selectedPages, pageIndex]);
    }
  };

  const handleSelectAll = () => {
    if (allSelected) {
      onChangeSelectedPages([]);
    } else {
      onChangeSelectedPages(pages.map((p) => p.pageIndex));
    }
  };

  const handleClear = () => {
    onChangeSelectedPages([]);
  };

  return (
    <section className="page-selector">
      <header className="page-selector__toolbar">
        <button type="button" onClick={handleSelectAll} disabled={pages.length === 0}>
          {allSelected ? "取消全选" : "全选"}
        </button>
        <button type="button" onClick={handleClear} disabled={selectedPages.length === 0}>
          清空选中
        </button>
        <span className="page-selector__summary">
          已选 {selectedPages.length} / {pages.length} 页
        </span>
      </header>
      <div className="page-selector__grid">
        {pages.map((page) => {
          const isSelected = selectedPages.includes(page.pageIndex);
          return (
            <button
              key={page.pageIndex}
              type="button"
              className={`page-selector__item${isSelected ? " page-selector__item--selected" : ""}`}
              onClick={() => togglePage(page.pageIndex)}
            >
              <img src={page.imageUrl} alt={`第 ${page.pageIndex + 1} 页`} />
              <span className="page-selector__label">{page.pageIndex + 1}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
}

