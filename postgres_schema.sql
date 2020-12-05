CREATE TABLE author( 
   author_name varchar(50) PRIMARY KEY,    
   dob varchar(50),    
   description varchar(30000)
);
CREATE TABLE quotes(
    quote_id INTEGER PRIMARY KEY,    
    author_name varchar(50),    
    quote varchar(3500)
);
CREATE TABLE tags( 
   quote_id INTEGER,    
   tag varchar(50)
);
