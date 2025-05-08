db = db.getSiblingDB("ecommerce");

db.clientes.insertMany([
  { _id: 1, nombre: "Ana", email: "ana@email.com", direccion: "Calle A 123" },
  { _id: 2, nombre: "Luis", email: "luis@email.com", direccion: "Calle B 456" },
]);

db.vendedores.insertMany([
  {
    _id: 1,
    nombre: "TechStore",
    email: "tech@store.com",
    categoria: "Electrónica",
  },
]);

db.administradores.insertOne({
  _id: 1,
  nombre: "Admin Juan",
  email: "admin@ecommerce.com",
});

db.productos.insertMany([
  { _id: 1, nombre: "Laptop", precio: 1200.0, vendedor_id: 1 },
  { _id: 2, nombre: "Mouse", precio: 20.0, vendedor_id: 1 },
]);

db.pedidos.insertOne({
  _id: 1,
  cliente_id: 1,
  productos: [1, 2],
  total: 1220.0,
  fecha: new Date(),
});

db.carritos.insertOne({
  _id: 1,
  cliente_id: 2,
  productos: [{ id: 2, cantidad: 1 }],
});

db.pagos.insertOne({
  _id: 1,
  pedido_id: 1,
  metodo: "tarjeta",
  estado: "completado",
  fecha: new Date(),
});

db.devoluciones.insertOne({
  _id: 1,
  pedido_id: 1,
  producto_id: 2,
  motivo: "Defectuoso",
});

db.mensajes.insertOne({
  _id: 1,
  de: "cliente:1",
  para: "vendedor:1",
  contenido: "¿Cuánto tarda el envío?",
  timestamp: new Date(),
});
