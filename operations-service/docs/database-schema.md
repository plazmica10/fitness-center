## Entity Relationships

```
trainers (1) ──────< (0..N) classes
rooms (1) ──────< (0..N) classes
classes (1) ──────< (0..N) attendances
classes (1) ──────< (0..N) payments
```
 <!-- (PlantUML) -->

```plantuml
@startuml
skinparam linetype ortho
skinparam roundcorner 10

entity "trainers" as trainers {
  * **trainer_id** : UUID <<PK>>
  --
  * name : String
  * specialization : String
  rating : Nullable(Float64)
}

entity "rooms" as rooms {
  * **room_id** : UUID <<PK>>
  --
  * name : String
  * capacity : Int32
  * has_equipment : UInt8
}

entity "classes" as classes {
  * **class_id** : UUID <<PK>>
  --
  * name : String
  trainer_id : Nullable(UUID) <<FK>>
  room_id : Nullable(UUID) <<FK>>
  * start_time : DateTime
  * end_time : DateTime
  capacity : Nullable(Int32)
  price : Nullable(Float64)
  description : Nullable(String)
}

entity "attendances" as attendances {
  * **event_id** : UUID <<PK>>
  --
  * class_id : UUID <<FK>>
  * member_id : UUID
  * timestamp : DateTime
  * status : String
}

entity "payments" as payments {
  * **payment_id** : UUID <<PK>>
  --
  * member_id : UUID
  * class_id : UUID <<FK>>
  * amount : Float64
  * timestamp : DateTime
}

' Relationships
trainers ||--o{ classes : "teaches"
rooms ||--o{ classes : "hosts"
classes ||--o{ attendances : "has"
classes ||--o{ payments : "receives"

@enduml
```
