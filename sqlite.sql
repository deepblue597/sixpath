CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    company TEXT,
    sector TEXT,
    is_me BOOLEAN DEFAULT 0, -- 0 for false, 1 for true
    -- only for is_me = 1
    username TEXT UNIQUE,
    password TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    linkedin_url TEXT,
    how_i_know_them TEXT,  -- "Met at conference", "College friend", etc.
    when_i_met_them DATE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Connections between people (bidirectional relationships)
CREATE TABLE IF NOT EXISTS connections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person1_id INTEGER NOT NULL,
    person2_id INTEGER NOT NULL,
    relationship TEXT,  -- "friend", "colleague", "mentor", "client", etc.
    strength INTEGER CHECK(strength >= 1 AND strength <= 5),  -- How strong the connection
    context TEXT,  -- How they know each other
    last_interaction DATE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (person1_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (person2_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(person1_id, person2_id)  -- Prevent duplicate connections
);

-- Referrals (linked to people who referred you)
CREATE TABLE IF NOT EXISTS referrals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    referrer_id INTEGER NOT NULL,  -- Person who referred you
    company TEXT NOT NULL,
    position TEXT,
    application_date DATE,
    interview_date DATE,
    status TEXT,  -- "pending", "rejected", "offered", "accepted"
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (referrer_id) REFERENCES users(id) ON DELETE CASCADE
);


-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_sector ON users(sector);
CREATE INDEX IF NOT EXISTS idx_users_company ON users(company);
CREATE INDEX IF NOT EXISTS idx_users_is_me ON users(is_me);
CREATE INDEX IF NOT EXISTS idx_connections_person1 ON connections(person1_id);
CREATE INDEX IF NOT EXISTS idx_connections_person2 ON connections(person2_id);

CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id);