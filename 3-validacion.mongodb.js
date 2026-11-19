// GreenPower: reglas $jsonSchema y pruebas inválidas
use("greenpower");
db.runCommand({collMod:"plantas",validator:{$jsonSchema:{bsonType:"object",required:["nombre","tecnologia","capacidad_mw"],properties:{nombre:{bsonType:"string",minLength:1},tecnologia:{bsonType:"string",minLength:1},capacidad_mw:{bsonType:["double","int","long","decimal"],minimum:0.000001}}}},validationLevel:"strict",validationAction:"error"});
print("Validacion aplicada a plantas.");
db.runCommand({collMod:"mantenimientos",validator:{$jsonSchema:{bsonType:"object",required:["tipo","fecha"],properties:{tipo:{bsonType:"string",enum:["preventivo","correctivo"]},fecha:{bsonType:"date"}}}},validationLevel:"strict",validationAction:"error"});
print("Validacion aplicada a mantenimientos.");
try { db.plantas.insertOne({_id:"PL-INVALIDA-01",tecnologia:"Solar",capacidad_mw:0}); print("ERROR: planta invalida aceptada"); } catch(e) { print("Prueba 1 superada: planta invalida rechazada."); print(e.message); }
try { db.mantenimientos.insertOne({_id:"MT-INVALIDO-01",planta_id:"PL-001",tipo:"predictivo",descripcion:"Prueba"}); print("ERROR: mantenimiento invalido aceptado"); } catch(e) { print("Prueba 2 superada: mantenimiento invalido rechazado."); print(e.message); }
print("Parte 3: validaciones finalizadas.");
