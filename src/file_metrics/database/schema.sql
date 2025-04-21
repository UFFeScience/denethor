CREATE TABLE file_metrics (
    id SERIAL PRIMARY KEY,
    tag VARCHAR(255) NOT NULL UNIQUE, -- Tag to identify the batch of metrics, must be unique
    file_name VARCHAR(255) NOT NULL, -- Name of the file
    file_size FLOAT NOT NULL, -- Size of the file in bytes
    duration_ms FLOAT NOT NULL, -- Duration in milliseconds (download or upload)
    metric_type VARCHAR(10) NOT NULL CHECK (metric_type IN ('download', 'upload')), -- 'download' or 'upload'
    normalized_duration_ms FLOAT, -- Normalized duration in milliseconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp of record creation
    CONSTRAINT unique_tag_file_name_metric_type UNIQUE (tag, file_name, metric_type) -- Ensure tag + file_name is unique
);

-- Drop the unique constraint on the 'tag' and 'file_name' columns
ALTER TABLE file_metrics DROP CONSTRAINT unique_tag_file_name;

-- Add the unique constraint for the combination of 'tag', 'file_name', and 'metric_type'
ALTER TABLE file_metrics ADD CONSTRAINT unique_tag_file_name_metric_type UNIQUE (tag, file_name, metric_type);

-- Add the normalized_duration_ms column to the file_metrics table
ALTER TABLE file_metrics ADD COLUMN normalized_duration_ms FLOAT;


select file_name, metric_type,
		max(duration_ms),
		min(duration_ms),
		avg(duration_ms),
		max(duration_ms) - min(duration_ms) as dif,
		max(duration_ms) / avg(duration_ms)
from file_metrics
group by file_name, metric_type
order by dif desc;


-- 'file_name'	'metric_type'	'max'				'max_avg'
-- 'tree_ORTHOMCL557.nexus'	'upload'	556.8202269998892				2.4741913565057274
-- 'ORTHOMCL1313'	'download'	359.8009770000772				1.8967380462455041
-- 'ORTHOMCL1352'	'download'	319.9168499999985				1.6011326974263929
-- 'tree_ORTHOMCL1034.nexus'	'download'	319.7804339999948				1.7151949918250178
-- 'tree_ORTHOMCL1005_Inner4.nexus'	'download'	299.75787700000467				1.666808260863533
-- 'tree_ORTHOMCL1977.nexus'	'upload'	376.9775370000161				1.2081675267185983
-- 'tree_ORTHOMCL1029_Inner2.nexus'	'download'	459.797867000006				1.169437515215318
-- 'tree_ORTHOMCL1378.nexus'	'download'	439.7415679999881				1.1577627629132115
-- 'ORTHOMCL1'	'download'	197.6797730000044				1.252074376563339
-- 'ORTHOMCL1985'	'download'	379.7998769999822				1.0983916086633052


select file_name, metric_type,
		max(normalized_duration_ms) max_nd,
		min(normalized_duration_ms) min_nd,
		avg(normalized_duration_ms) avg_nd,
		max(normalized_duration_ms) - min(normalized_duration_ms) dif_nd
from file_metrics
group by file_name, metric_type
order by dif_nd desc;


-- Update normalized_duration_ms for each record
UPDATE file_metrics
SET normalized_duration_ms = duration_ms / 2.4741913565057274
WHERE file_name = 'tree_ORTHOMCL557.nexus' AND metric_type = 'upload' AND duration_ms = 556.8202269998892;

UPDATE file_metrics
SET normalized_duration_ms = duration_ms / 1.8967380462455041
WHERE file_name = 'ORTHOMCL1313' AND metric_type = 'download' AND duration_ms = 359.8009770000772;

UPDATE file_metrics
SET normalized_duration_ms = duration_ms / 1.6011326974263929
WHERE file_name = 'ORTHOMCL1352' AND metric_type = 'download' AND duration_ms = 319.9168499999985;

UPDATE file_metrics
SET normalized_duration_ms = duration_ms / 1.7151949918250178
WHERE file_name = 'tree_ORTHOMCL1034.nexus' AND metric_type = 'download' AND duration_ms = 319.7804339999948;

UPDATE file_metrics
SET normalized_duration_ms = duration_ms / 1.666808260863533
WHERE file_name = 'tree_ORTHOMCL1005_Inner4.nexus' AND metric_type = 'download' AND duration_ms = 299.75787700000467;

UPDATE file_metrics
SET normalized_duration_ms = duration_ms / 1.2081675267185983
WHERE file_name = 'tree_ORTHOMCL1977.nexus' AND metric_type = 'upload' AND duration_ms = 376.9775370000161;

UPDATE file_metrics
SET normalized_duration_ms = duration_ms / 1.169437515215318
WHERE file_name = 'tree_ORTHOMCL1029_Inner2.nexus' AND metric_type = 'download' AND duration_ms = 459.797867000006;

UPDATE file_metrics
SET normalized_duration_ms = duration_ms / 1.1577627629132115
WHERE file_name = 'tree_ORTHOMCL1378.nexus' AND metric_type = 'download' AND duration_ms = 439.7415679999881;

UPDATE file_metrics
SET normalized_duration_ms = duration_ms / 1.252074376563339
WHERE file_name = 'ORTHOMCL1' AND metric_type = 'download' AND duration_ms = 197.6797730000044;

UPDATE file_metrics
SET normalized_duration_ms = duration_ms / 1.0983916086633052
WHERE file_name = 'ORTHOMCL1985' AND metric_type = 'download' AND duration_ms = 379.7998769999822;



UPDATE file_metrics
SET normalized_duration_ms = duration_ms
WHERE normalized_duration_ms is null;



