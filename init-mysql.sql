CREATE DATABASE IF NOT EXISTS entreprise;
USE entreprise;

CREATE TABLE IF NOT EXISTS employes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    poste VARCHAR(100) NOT NULL,
    salaire DECIMAL(10,2) NOT NULL,
    department VARCHAR(100) NOT NULL,
    date_embauche DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO employes (nom, prenom, email, poste, salaire, department) VALUES
('Dupont', 'Jean', 'jean.dupont@entreprise.com', 'Développeur', 45000.00, 'IT'),
('Martin', 'Marie', 'marie.martin@entreprise.com', 'Chef de projet', 55000.00, 'Management'),
('Bernard', 'Pierre', 'pierre.bernard@entreprise.com', 'Analyste', 40000.00, 'Finance');