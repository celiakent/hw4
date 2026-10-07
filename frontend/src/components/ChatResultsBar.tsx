import { Link } from 'react-router-dom'
import { formatPrice, imageUrl } from '../api'
import { useChatResults } from '../chatResults'

/**
 * Shows the product matches the chatbot found, on the page itself (not just in the
 * chat bubble). Every card links to the Problem 3 single-item page.
 */
export default function ChatResultsBar() {
  const { query, products, clear } = useChatResults()

  if (products.length === 0) return null

  return (
    <section className="chat-results" aria-label="Products from your chat">
      <div className="chat-results-head">
        <div>
          <p className="eyebrow">From the chat</p>
          <h2>{query ? `Matches for “${query}”` : 'Matches from your chat'}</h2>
        </div>
        <button type="button" className="chat-results-clear" onClick={clear}>
          Clear
        </button>
      </div>
      <div className="product-grid">
        {products.map((p) => (
          <Link to={`/products/${p.product_id}`} className="product-card" key={p.product_id}>
            <div className="product-card-image">
              <img src={imageUrl(p.image_url)} alt={p.name} loading="lazy" />
            </div>
            <div className="product-card-body">
              <h3>{p.name}</h3>
              <p className="product-card-colors">{p.garment_type}</p>
            </div>
            <div className="product-card-foot">
              <span className="product-card-action">View</span>
              <span className="price">{formatPrice(p.price)}</span>
            </div>
          </Link>
        ))}
      </div>
    </section>
  )
}
