import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { getProducts, type Product } from '../api'
import ProductCard from '../components/ProductCard'
import { COLLECTIONS } from '../collections'

const searchText = (p: Product) =>
  [p.name, p.garment_type, p.description, ...p.colors, ...p.search_tags].join(' ').toLowerCase()

const escapeRegex = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')

const PRICE_RANGES = [
  { key: 'all', label: 'Any price', test: () => true },
  { key: 'u40', label: 'Under $40', test: (p: Product) => p.price < 40 },
  { key: 'u60', label: 'Under $60', test: (p: Product) => p.price < 60 },
  { key: 'u80', label: 'Under $80', test: (p: Product) => p.price < 80 },
]

type SortKey = 'featured' | 'price-asc' | 'price-desc'

export default function Products() {
  const [products, setProducts] = useState<Product[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [priceRange, setPriceRange] = useState('all')
  const [sort, setSort] = useState<SortKey>('featured')
  const [inStockOnly, setInStockOnly] = useState(false)
  const [searchParams] = useSearchParams()
  const collection = COLLECTIONS.find((c) => c.slug === searchParams.get('collection'))

  useEffect(() => {
    getProducts()
      .then(setProducts)
      .catch(() => setError('We couldn’t load products. Is the backend running?'))
      .finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => {
    let list = products
    if (collection) {
      const pattern = new RegExp(`\\b(${collection.keywords.map(escapeRegex).join('|')})`, 'i')
      list = list.filter((p) => pattern.test([p.name, p.garment_type, ...p.search_tags].join(' ')))
    }
    const q = query.trim().toLowerCase()
    if (q) list = list.filter((p) => searchText(p).includes(q))

    const range = PRICE_RANGES.find((r) => r.key === priceRange)
    if (range) list = list.filter(range.test)

    if (inStockOnly) list = list.filter((p) => p.in_stock)

    if (sort === 'price-asc') list = [...list].sort((a, b) => a.price - b.price)
    else if (sort === 'price-desc') list = [...list].sort((a, b) => b.price - a.price)

    return list
  }, [products, query, collection, priceRange, sort, inStockOnly])

  return (
    <div className="page">
      <div className="page-header">
        <h1>{collection ? collection.title : 'Shop'}</h1>
        <div className="filters">
          <Link to="/products" className={`chip${collection ? '' : ' active'}`}>All</Link>
          {COLLECTIONS.map((c) => (
            <Link
              key={c.slug}
              to={`/products?collection=${c.slug}`}
              className={`chip${collection?.slug === c.slug ? ' active' : ''}`}
            >
              {c.title}
            </Link>
          ))}
        </div>
      </div>

      <div className="toolbar">
        <input
          className="search"
          type="search"
          placeholder="Search by name, color, sport…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <label className="toolbar-field">
          <span>Price</span>
          <select value={priceRange} onChange={(e) => setPriceRange(e.target.value)}>
            {PRICE_RANGES.map((r) => (
              <option key={r.key} value={r.key}>{r.label}</option>
            ))}
          </select>
        </label>
        <label className="toolbar-field">
          <span>Sort</span>
          <select value={sort} onChange={(e) => setSort(e.target.value as SortKey)}>
            <option value="featured">Featured</option>
            <option value="price-asc">Price: low to high</option>
            <option value="price-desc">Price: high to low</option>
          </select>
        </label>
        <label className="toolbar-check">
          <input
            type="checkbox"
            checked={inStockOnly}
            onChange={(e) => setInStockOnly(e.target.checked)}
          />
          In stock only
        </label>
      </div>

      {loading && <p className="status">Loading products…</p>}
      {error && <p className="status error">{error}</p>}
      {!loading && !error && (
        <>
          <p className="result-count">{filtered.length} products</p>
          {filtered.length === 0 ? (
            <p className="status">No products match those filters. Try widening your search.</p>
          ) : (
            <div className="product-grid">
              {filtered.map((p) => (
                <ProductCard key={p.product_id} product={p} />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  )
}
