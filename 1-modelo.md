# GreenPower — Modelo de datos NoSQL

## Descripción
GreenPower administra plantas renovables, equipos, estaciones, producción, mantenimientos, contratos, subestaciones y redes. La base de datos es `greenpower`. Se parte de la colección principal `plantas` e incluye plantas de ejemplo como Solar Wayuu, Hidro Alto Cauca, Eólica Magdalena, Eólica del Norte y Solar del Llano.

> **Importante:** el archivo o diagrama relacional original no fue adjuntado en esta fase. La correspondencia siguiente se basa en las ocho entidades identificadas del proyecto[cite: 13]. Antes de la entrega final, contrástala con tu diagrama relacional original y ajusta cardinalidades o claves si difieren[cite: 13].

## Seis consultas importantes
1. Consultar una planta por ID o departamento con sus equipos y estaciones[cite: 13].
2. Sumar la energía generada por tecnología y mes[cite: 13].
3. Contar los equipos por tipo y estado[cite: 13].
4. Consultar mantenimientos por planta mostrando el nombre de la planta[cite: 13].
5. Consultar contratos activos, clientes y energía comprometida[cite: 13].
6. Consultar subestaciones y sus redes de distribución[cite: 13].

## Tablas/entidades relacionales identificadas
`Planta`, `Equipo`, `Estacion`, `Produccion`, `Subestacion`, `Red_Distribucion`, `Contrato`, `Mantenimiento`[cite: 13].

Relaciones lógicas consideradas: Planta 1:N Equipo; Planta 1:N Estacion; Planta 1:N Produccion; Planta 1:N Mantenimiento; Planta 1:N Contrato; Planta 1:N Subestacion; Subestacion 1:N Red_Distribucion[cite: 13].

## Colecciones (5, menos que las 8 tablas)
| Colección | Contenido |
|---|---|
| `plantas` | Datos de planta, ubicación, equipos y estaciones embebidos[cite: 13] |
| `produccion` | Registros históricos de generación, referencia `planta_id`[cite: 13] |
| `mantenimientos` | Historial de mantenimientos, referencia `planta_id`[cite: 13] |
| `contratos` | Contratos, referencia `planta_id`[cite: 13] |
| `subestaciones` | Subestaciones con redes embebidas, referencia `planta_id`[cite: 13] |

## Decisiones de embebido/referencia
| Relación | Decisión | Justificación |
|---|---|---|
| Planta–Equipo | Embebida en `plantas.equipos`[cite: 13] | Se consulta como parte de la ficha y su tamaño es controlado[cite: 13]. |
| Planta–Estacion | Embebida en `plantas.estaciones`[cite: 13] | Información descriptiva que se consulta junto con la planta[cite: 13]. |
| Planta–Produccion | Referencia `planta_id`[cite: 13] | El histórico crece continuamente; evita arreglos ilimitados[cite: 13]. |
| Planta–Mantenimiento | Referencia `planta_id`[cite: 13] | Historial independiente y creciente[cite: 13]. |
| Planta–Contrato | Referencia `planta_id`[cite: 13] | Tiene ciclo de vida y consultas independientes[cite: 13]. |
| Planta–Subestacion | Referencia `planta_id`[cite: 13] | Infraestructura consultable por separado[cite: 13]. |
| Subestacion–Red_Distribucion | Embebida en `subestaciones.redes_distribucion`[cite: 13] | Las redes se muestran con su subestación y son un conjunto acotado[cite: 13]. |

## Documentos completos de ejemplo
### `plantas`
```javascript
{
  _id: "PL-001",
  nombre: "Solar Wayuu",
  tecnologia: "Solar",
  capacidad_mw: 120,
  departamento: "La Guajira",
  municipio: "Uribia",
  estado: "Operativa",
  ubicacion: { latitud: 4.81, longitud: -76.61 },
  fecha_puesta_marcha: ISODate("2022-02-15T00:00:00Z"),
  mantenimientos_realizados: 1,
  equipos: [
    { equipo_id: "EQ-001-1", tipo: "Panel solar", estado: "Operativo", marca: "Trina" },
    { equipo_id: "EQ-001-2", tipo: "Panel solar", estado: "Operativo", marca: "Jinko" },
    { equipo_id: "EQ-001-3", tipo: "Inversor", estado: "Operativo", marca: "Huawei" },
    { equipo_id: "EQ-001-4", tipo: "Inversor", estado: "Fuera de servicio", marca: "SMA" }
  ],
  estaciones: [
    { estacion_id: "ES-001-1", nombre: "Estacion Solar Principal", estado: "Operativa" }
  ]
}