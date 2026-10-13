import React, { useState, useEffect } from 'react';
import api from '../api';
import { useToast } from '../components/Toast';
import { Package, Plus, Trash2, Edit3, Search } from 'lucide-react';

export default function ProductCatalog() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const addToast = useToast();

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newProduct, setNewProduct] = useState({ name: '', brand: '', category: '', warranty_months: 12 });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const { data } = await api.get('/products');
      setProducts(data);
    } catch (err) {
      addToast('Failed to load products', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const { data } = await api.post('/products', newProduct);
      setProducts(prev => [...prev, data]);
      setIsModalOpen(false);
      setNewProduct({ name: '', brand: '', category: '', warranty_months: 12 });
      addToast('Product added successfully', 'success');
    } catch (err) {
      addToast('Failed to add product', 'error');
    } finally {
      setSaving(false);
    }
  };

  const filteredProducts = products.filter(p => 
    p.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    p.brand.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="flex items-center gap-2 m-0">
            <Package className="text-primary" /> Product Catalog
          </h2>
          <p className="mt-2">Manage products, brands, and warranty lengths.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={18} /> Add Product
        </button>
      </div>

      <div className="card mb-6 p-4 flex gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted" size={18} />
          <input 
            type="text" 
            placeholder="Search products or brands..." 
            className="form-input pl-10"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="data-table-container">
        {loading ? (
          <div className="p-8 text-center">Loading products...</div>
        ) : filteredProducts.length === 0 ? (
          <div className="p-8 text-center text-muted">No products found.</div>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>Brand</th>
                <th>Product Name</th>
                <th>Category</th>
                <th>Warranty (Months)</th>
                <th className="text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredProducts.map(product => (
                <tr key={product.id}>
                  <td className="font-medium">{product.brand}</td>
                  <td>{product.name}</td>
                  <td><span className="badge badge-neutral">{product.category}</span></td>
                  <td>{product.warranty_months} mo</td>
                  <td className="text-right">
                    <button className="btn btn-secondary mr-2" style={{padding: '6px 12px'}} title="Edit">
                      <Edit3 size={14} />
                    </button>
                    <button className="btn btn-danger" style={{padding: '6px 12px'}} title="Delete">
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="card w-full max-w-md">
            <h3 className="mb-4">Add New Product</h3>
            <form onSubmit={handleCreateProduct} className="flex-col gap-4">
              <div className="flex-col gap-1">
                <label className="text-sm font-semibold">Brand</label>
                <input required type="text" className="form-input" value={newProduct.brand} onChange={e => setNewProduct({...newProduct, brand: e.target.value})} placeholder="e.g. HP" />
              </div>
              <div className="flex-col gap-1">
                <label className="text-sm font-semibold">Product Name / Series</label>
                <input required type="text" className="form-input" value={newProduct.name} onChange={e => setNewProduct({...newProduct, name: e.target.value})} placeholder="e.g. Spectre x360" />
              </div>
              <div className="flex-col gap-1">
                <label className="text-sm font-semibold">Category</label>
                <input required type="text" className="form-input" value={newProduct.category} onChange={e => setNewProduct({...newProduct, category: e.target.value})} placeholder="e.g. Laptop" />
              </div>
              <div className="flex-col gap-1">
                <label className="text-sm font-semibold">Warranty Length (Months)</label>
                <input required type="number" min="1" className="form-input" value={newProduct.warranty_months} onChange={e => setNewProduct({...newProduct, warranty_months: parseInt(e.target.value)})} />
              </div>
              
              <div className="flex justify-end gap-3 mt-6">
                <button type="button" className="btn btn-secondary" onClick={() => setIsModalOpen(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Saving...' : 'Add Product'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
