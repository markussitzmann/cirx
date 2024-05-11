BEGIN;

CREATE INDEX IF NOT EXISTS cir_index_block1_index ON cir_inchi(block1);
CREATE INDEX IF NOT EXISTS cir_index_block2_index ON cir_inchi(block2);
CREATE INDEX IF NOT EXISTS cir_index_block3_index ON cir_inchi(block3);

COMMIT;

