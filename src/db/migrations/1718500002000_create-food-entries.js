exports.up = (pgm) => {
  pgm.createTable('food_entries', {
    id: { type: 'serial', primaryKey: true },
    name: { type: 'varchar(200)', notNull: true },
    calories: { type: 'integer', notNull: true, check: 'calories > 0' },
    logged_at: { type: 'timestamp', notNull: true, default: pgm.func('now()') },
  });
};

exports.down = (pgm) => {
  pgm.dropTable('food_entries');
};
