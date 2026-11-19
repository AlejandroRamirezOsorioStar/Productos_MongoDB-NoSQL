// GreenPower: indices y explain("executionStats") antes/despues
use("greenpower");
print("INDICE 1: plantas por tecnologia y capacidad");
print("ANTES:"); printjson(db.plantas.find({tecnologia:"Solar",capacidad_mw:{$gt:50}}).explain("executionStats"));
db.plantas.createIndex({tecnologia:1,capacidad_mw:-1},{name:"idx_plantas_tecnologia_capacidad"});
print("DESPUES:"); printjson(db.plantas.find({tecnologia:"Solar",capacidad_mw:{$gt:50}}).explain("executionStats"));
print("Justificacion: indice compuesto para filtrar por tecnologia y capacidad.");
print("INDICE 2: produccion por planta y fecha");
const desde=ISODate("2026-10-01T00:00:00Z"), hasta=ISODate("2026-11-01T00:00:00Z");
print("ANTES:"); printjson(db.produccion.find({planta_id:"PL-001",fecha:{$gte:desde,$lt:hasta}}).sort({fecha:-1}).explain("executionStats"));
db.produccion.createIndex({planta_id:1,fecha:-1},{name:"idx_produccion_planta_fecha"});
print("DESPUES:"); printjson(db.produccion.find({planta_id:"PL-001",fecha:{$gte:desde,$lt:hasta}}).sort({fecha:-1}).explain("executionStats"));
print("Justificacion: localiza la produccion de una planta en un rango y ordena por fecha.");
print("Compare winningPlan (COLLSCAN/IXSCAN), totalDocsExamined y executionTimeMillis. Con pocos documentos el tiempo puede ser parecido.");
