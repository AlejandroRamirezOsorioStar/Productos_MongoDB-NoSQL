// GreenPower: cinco reportes de agregacion
use("greenpower");
// REPORTE 1 (asignado): ¿Cuanta energia se genero por tecnologia y por mes?
print("\nREPORTE 1 - Energia por tecnologia y mes");
printjson(db.produccion.aggregate([{$lookup:{from:"plantas",localField:"planta_id",foreignField:"_id",as:"planta"}},{$unwind:"$planta"},{$group:{_id:{tecnologia:"$planta.tecnologia",mes:{$dateToString:{format:"%Y-%m",date:"$fecha"}}},energia_total_mwh:{$sum:"$energia_mwh"},registros:{$sum:1}}},{$project:{_id:0,tecnologia:"$_id.tecnologia",mes:"$_id.mes",energia_total_mwh:1,registros:1}},{$sort:{mes:-1,energia_total_mwh:-1}}]).toArray());
// REPORTE 2 (asignado): ¿Cuantos equipos hay por tipo y estado? $unwind separa cada equipo.
print("\nREPORTE 2 - Muestra parcial despues de $unwind");
printjson(db.plantas.aggregate([{$unwind:"$equipos"},{$project:{_id:0,planta:"$nombre",tipo:"$equipos.tipo",estado:"$equipos.estado"}},{$limit:8}]).toArray());
print("Resultado agrupado por tipo y estado:");
printjson(db.plantas.aggregate([{$unwind:"$equipos"},{$group:{_id:{tipo:"$equipos.tipo",estado:"$equipos.estado"},cantidad_equipos:{$sum:1}}},{$project:{_id:0,tipo:"$_id.tipo",estado:"$_id.estado",cantidad_equipos:1}},{$sort:{tipo:1,estado:1}}]).toArray());
// REPORTE 3 (asignado): ¿Que mantenimientos tiene cada planta? $lookup recupera su nombre.
print("\nREPORTE 3 - Mantenimientos por planta");
printjson(db.mantenimientos.aggregate([{$lookup:{from:"plantas",localField:"planta_id",foreignField:"_id",as:"planta"}},{$unwind:"$planta"},{$group:{_id:{id:"$planta._id",nombre:"$planta.nombre"},cantidad:{$sum:1},tipos:{$addToSet:"$tipo"}}},{$project:{_id:0,planta_id:"$_id.id",planta:"$_id.nombre",cantidad_mantenimientos:"$cantidad",tipos:1}},{$sort:{cantidad_mantenimientos:-1}}]).toArray());
// REPORTE 4 (propio): ¿Cuales son las cinco plantas con mayor generacion en octubre de 2026?
print("\nREPORTE 4 - Top 5 generacion octubre 2026");
printjson(db.produccion.aggregate([{$match:{fecha:{$gte:ISODate("2026-10-01T00:00:00Z"),$lt:ISODate("2026-11-01T00:00:00Z")}}},{$group:{_id:"$planta_id",energia_total_mwh:{$sum:"$energia_mwh"}}},{$lookup:{from:"plantas",localField:"_id",foreignField:"_id",as:"planta"}},{$unwind:"$planta"},{$project:{_id:0,planta:"$planta.nombre",tecnologia:"$planta.tecnologia",energia_total_mwh:1}},{$sort:{energia_total_mwh:-1}},{$limit:5}]).toArray());
// REPORTE 5 (propio): ¿Cuantos contratos y MWh comprometidos hay por estado?
print("\nREPORTE 5 - Contratos por estado");
printjson(db.contratos.aggregate([{$group:{_id:"$estado",cantidad_contratos:{$sum:1},energia_comprometida_mwh:{$sum:"$energia_contratada_mwh"}}},{$project:{_id:0,estado:"$_id",cantidad_contratos:1,energia_comprometida_mwh:1}},{$sort:{cantidad_contratos:-1}}]).toArray());
print("Cinco reportes finalizados.");
