"""
Data management and local storage
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.account import Account, Portfolio
from models.position import Position
from models.order import Order
from models.strategy import Strategy

class DataManager:
    """Manages local data storage using SQLite"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "data" / "database.db"
        else:
            db_path = Path(db_path)
            
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
    def _init_database(self):
        """Initialize database tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Account history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS account_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        address TEXT NOT NULL,
                        account_value REAL NOT NULL,
                        available_balance REAL NOT NULL,
                        margin_used REAL NOT NULL,
                        total_pnl REAL NOT NULL,
                        data_json TEXT
                    )
                ''')
                
                # Orders table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS orders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        order_id TEXT UNIQUE NOT NULL,
                        coin TEXT NOT NULL,
                        side TEXT NOT NULL,
                        size REAL NOT NULL,
                        price REAL,
                        order_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        filled_size REAL DEFAULT 0,
                        remaining_size REAL DEFAULT 0,
                        average_fill_price REAL DEFAULT 0,
                        timestamp TEXT NOT NULL,
                        filled_at TEXT,
                        data_json TEXT
                    )
                ''')
                
                # Strategies table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS strategies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        strategy_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        coin TEXT,
                        strategy_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        config_json TEXT,
                        performance_json TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                ''')
                
                # Trade history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS trades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        trade_id TEXT UNIQUE NOT NULL,
                        order_id TEXT,
                        coin TEXT NOT NULL,
                        side TEXT NOT NULL,
                        size REAL NOT NULL,
                        price REAL NOT NULL,
                        fee REAL DEFAULT 0,
                        timestamp TEXT NOT NULL,
                        strategy_id TEXT,
                        data_json TEXT
                    )
                ''')
                
                conn.commit()
                self.logger.info("Database initialized successfully")
                
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            
    def save_account_snapshot(self, account: Account):
        """Save account snapshot to history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO account_history 
                    (timestamp, address, account_value, available_balance, margin_used, total_pnl, data_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.utcnow().isoformat(),
                    account.address,
                    account.account_value,
                    account.available_balance,
                    account.margin_used,
                    account.total_pnl,
                    json.dumps(account.to_dict())
                ))
                conn.commit()
                self.logger.info("Account snapshot saved")
        except Exception as e:
            self.logger.error(f"Failed to save account snapshot: {e}")
            
    def get_account_history(self, days: int = 30) -> List[Dict]:
        """Get account history for specified days"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM account_history 
                    WHERE timestamp > datetime('now', '-{} days')
                    ORDER BY timestamp DESC
                '''.format(days))
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                return [dict(zip(columns, row)) for row in rows]
                
        except Exception as e:
            self.logger.error(f"Failed to get account history: {e}")
            return []
            
    def save_order(self, order: Order):
        """Save order to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO orders 
                    (order_id, coin, side, size, price, order_type, status, filled_size, 
                     remaining_size, average_fill_price, timestamp, filled_at, data_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    order.order_id,
                    order.coin,
                    order.side.value,
                    order.size,
                    order.price,
                    order.order_type.value,
                    order.status.value,
                    order.filled_size,
                    order.remaining_size,
                    order.average_fill_price,
                    order.timestamp.isoformat() if order.timestamp else None,
                    order.filled_at.isoformat() if order.filled_at else None,
                    json.dumps(order.to_dict())
                ))
                conn.commit()
                self.logger.info(f"Order {order.order_id} saved")
        except Exception as e:
            self.logger.error(f"Failed to save order: {e}")
            
    def get_orders(self, status: str = None, limit: int = 100) -> List[Order]:
        """Get orders from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if status:
                    cursor.execute('''
                        SELECT data_json FROM orders 
                        WHERE status = ? 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (status, limit))
                else:
                    cursor.execute('''
                        SELECT data_json FROM orders 
                        ORDER BY timestamp DESC 
                        LIMIT ?
                    ''', (limit,))
                
                rows = cursor.fetchall()
                orders = []
                
                for row in rows:
                    try:
                        order_data = json.loads(row[0])
                        orders.append(Order.from_dict(order_data))
                    except Exception as e:
                        self.logger.error(f"Failed to parse order data: {e}")
                        
                return orders
                
        except Exception as e:
            self.logger.error(f"Failed to get orders: {e}")
            return []
            
    def save_strategy(self, strategy: Strategy):
        """Save strategy to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO strategies 
                    (strategy_id, name, description, coin, strategy_type, status, 
                     config_json, performance_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    strategy.strategy_id,
                    strategy.name,
                    strategy.description,
                    strategy.coin,
                    strategy.strategy_type.value,
                    strategy.status.value,
                    json.dumps(strategy.config.to_dict()),
                    json.dumps(strategy.performance.to_dict()),
                    strategy.created_at.isoformat(),
                    strategy.updated_at.isoformat()
                ))
                conn.commit()
                self.logger.info(f"Strategy {strategy.name} saved")
        except Exception as e:
            self.logger.error(f"Failed to save strategy: {e}")
            
    def get_strategies(self) -> List[Strategy]:
        """Get all strategies from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM strategies ORDER BY updated_at DESC')
                
                rows = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                strategies = []
                
                for row in rows:
                    try:
                        row_dict = dict(zip(columns, row))
                        
                        # Parse JSON fields
                        config_data = json.loads(row_dict['config_json']) if row_dict['config_json'] else {}
                        performance_data = json.loads(row_dict['performance_json']) if row_dict['performance_json'] else {}
                        
                        # Create strategy dict
                        strategy_data = {
                            'strategy_id': row_dict['strategy_id'],
                            'name': row_dict['name'],
                            'description': row_dict['description'],
                            'coin': row_dict['coin'],
                            'strategy_type': row_dict['strategy_type'],
                            'status': row_dict['status'],
                            'config': config_data,
                            'performance': performance_data,
                            'created_at': row_dict['created_at'],
                            'updated_at': row_dict['updated_at']
                        }
                        
                        strategies.append(Strategy.from_dict(strategy_data))
                        
                    except Exception as e:
                        self.logger.error(f"Failed to parse strategy data: {e}")
                        
                return strategies
                
        except Exception as e:
            self.logger.error(f"Failed to get strategies: {e}")
            return []
            
    def delete_strategy(self, strategy_id: str) -> bool:
        """Delete strategy from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM strategies WHERE strategy_id = ?', (strategy_id,))
                conn.commit()
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Strategy {strategy_id} deleted")
                    return True
                else:
                    self.logger.warning(f"Strategy {strategy_id} not found")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Failed to delete strategy: {e}")
            return False
            
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Cleanup old data from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Clean old account history
                cursor.execute('''
                    DELETE FROM account_history 
                    WHERE timestamp < datetime('now', '-{} days')
                '''.format(days_to_keep))
                
                # Clean old completed orders
                cursor.execute('''
                    DELETE FROM orders 
                    WHERE status IN ('filled', 'cancelled') 
                    AND timestamp < datetime('now', '-{} days')
                '''.format(days_to_keep))
                
                conn.commit()
                self.logger.info(f"Cleaned data older than {days_to_keep} days")
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            
    def get_database_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Count records in each table
                tables = ['account_history', 'orders', 'strategies', 'trades']
                for table in tables:
                    cursor.execute(f'SELECT COUNT(*) FROM {table}')
                    stats[table] = cursor.fetchone()[0]
                    
                return stats
                
        except Exception as e:
            self.logger.error(f"Failed to get database stats: {e}")
            return {}