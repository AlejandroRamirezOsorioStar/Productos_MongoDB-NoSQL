// GreenPower: transaccion multidocumento. Requiere Atlas o replica set (no standalone).
use("greenpower");
const session=db.getMongo().startSession(); const sdb=session.getDatabase("greenpower");
function registrarMantenimiento(plantaId,mtId,forzarFallo){
  session.startTransaction({readConcern:{level:"snapshot"},writeConcern:{w:"majority"}});
  try {
    sdb.mantenimientos.insertOne({_id:mtId,planta_id:plantaId,tipo:"preventivo",fecha:new Date(),descripcion:"Mantenimiento registrado en transaccion",responsable:"Equipo GreenPower",estado:"Programado"});
    const idUpdate=forzarFallo?"PLANTA-INEXISTENTE":plantaId;
    const r=sdb.plantas.updateOne({_id:idUpdate},{$inc:{mantenimientos_realizados:1}});
    if(r.matchedCount!==1) throw new Error("No se encontro la planta para actualizar; se aborta.");
    session.commitTransaction(); print("COMMIT: mantenimiento insertado y planta actualizada."); return true;
  } catch(e) { session.abortTransaction(); print("ABORT: "+e.message); return false; }
}
print("PRUEBA DE REVERSIÓN");
const antes=sdb.mantenimientos.countDocuments({_id:"MT-ROLLBACK-01"});
registrarMantenimiento("PL-001","MT-ROLLBACK-01",true);
const despues=sdb.mantenimientos.countDocuments({_id:"MT-ROLLBACK-01"});
print("Antes="+antes+"; despues del abort="+despues);
if(antes===0 && despues===0) print("PRUEBA SUPERADA: el insert fue revertido y no quedó guardado."); else print("REVISAR resultado de rollback.");
print("PRUEBA DE CONFIRMACIÓN");
registrarMantenimiento("PL-001","MT-COMMIT-01",false);
print("Documento confirmado: "+sdb.mantenimientos.countDocuments({_id:"MT-COMMIT-01"}));
session.endSession();
