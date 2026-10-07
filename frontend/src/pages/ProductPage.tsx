import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { formatPrice, getProduct, imageUrl, type ProductDetail } from '../api'

function stockLabel(quantity: number) {
  if (quantity === 0) return 'Sold out'
  if (quantity <= 5) return `Only ${quantity} left`
  return `${quantity} in stock`
}

export default function ProductPage() {
  const { productId } = useParams()
  const [product, setProduct] = useState<ProductDetail | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedSize, setSelectedSize] = useState<string | null>(null)

  useEffect(() => {
    if (!productId) return
    setProduct(null)
    setError(null)
    setSelectedSize(null)
    getProduct(productId)
      .then(setProduct)
      .catch(() => setError('We couldn’t find that product.'))
  }, [productId])

  if (error) {
    return (
      <div className="page">
        <p className="status error">{error}</p>
        <Link to="/products">← Back to all products</Link>
      </div>
    )
  }

  if (!product) return <div className="page"><p className="status">Loading…</p></div>

  const totalStock = product.sizes.reduce((sum, s) => sum + s.quantity, 0)
  const selected = product.sizes.find((s) => s.size === selectedSize)

  return (
    <div className="page">
      <Link to="/products" className="back-link">← Back to all products</Link>
      <div className="product-detail">
        <div className="product-detail-image">
          <img src={imageUrl(product.image_url)} alt={product.name} />
        </div>
        <div className="product-detail-info">
          <p className="eyebrow">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="price large">{formatPrice(product.price)}</p>
          <p className="description">{product.description}</p>

          <div className="detail-section">
            <h2>Size</h2>
            <div className="size-grid">
              {product.sizes.map((s) => (
                <button
                  key={s.size}
                  className={`size-option${selectedSize === s.size ? ' selected' : ''}`}
                  disabled={s.quantity === 0}
                  onClick={() => setSelectedSize(s.size)}
                >
                  <span className="size-name">{s.size}</span>
                  <span className="size-stock">{stockLabel(s.quantity)}</span>
                </button>
              ))}
            </div>
            <p className="stock-note">
              {selected
                ? `${selected.size}: ${stockLabel(selected.quantity)}`
                : totalStock > 0
                  ? 'Select a size to check availability.'
                  : 'This item is currently sold out.'}
            </p>
          </div>

          <div className="tags">
            {product.search_tags.map((t) => (
              <span key={t} className="tag">{t}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
