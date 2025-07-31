UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'Ã¤', 'ä');


SELECT YourColumn FROM YourTable WHERE YourColumn LIKE '%Ã¤%' OR YourColumn LIKE '%Ã¶%' ...


-- Replace corrupted characters with correct Unicode equivalents
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'Ã¤', 'ä');
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'Ã¶', 'ö');
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'Ã¼', 'ü');
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'ÃŸ', 'ß');
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'Ã©', 'é');
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'Ã¨', 'è');
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'Ã±', 'ñ');
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'Ã³', 'ó');
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'Ĺ„', 'ń');
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'Ä…', 'ą');
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'Ĺ‚', 'ł');
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'Ã§', 'ç');
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'Ã¸', 'ø');
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'Ã†', 'Æ');
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'â‚¬', '€');

-- Replace ? with en dash
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, '?', N'–')
WHERE YourColumn LIKE '%?%';


-- Example: Replace corrupted dash in known phrase
UPDATE YourTable
SET YourColumn = REPLACE(YourColumn, 'New York ? London', N'New York – London');

