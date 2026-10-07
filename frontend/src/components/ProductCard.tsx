import { Link } from 'react-router-dom'
import { formatPrice, imageUrl, type Product } from '../api'

const LOW_STOCK = 15

function stockBadge(total: number): { label: string; tone: string } | null {
  if (total <= 0) return { label: 'Sold out', tone: 'out' }
  if (total <= LOW_STOCK) return { label: 'Only a few left', tone: 'low' }
  return null
}

export default function ProductCard({ product }: { product: Product }) {
  const badge = stockBadge(product.total_stock)

  return (
    <Link to={`/products/${product.product_id}`} className="product-card">
      <div className="product-card-image">
        {badge && <span className={`stock-badge ${badge.tone}`}>{badge.label}</span>}
        <img src={imageUrl(product.image_url)} alt={product.name} loading="lazy" />
      </div>
      <div className="product-card-body">
        <h3>{product.name}</h3>
        <p className="product-card-colors">{product.garment_type}</p>
      </div>
      <div className="product-card-foot">
        <span className="product-card-action">View</span>
        <span className="price">{formatPrice(product.price)}</span>
      </div>
    </Link>
  )
}
