# br-fleet-analysis
A demonstration of how to import and analyze changes in vehicle fleets in Brazil over the years.

The data sources are available at National Motor Vehicle Registry [Registro Nacional de Veículos Automotores - RENAVAM](https://dados.transportes.gov.br/dataset/registro-nacional-de-veiculos-automotores-renavam).

FIPE, avaible in Kaggle [Tabela Fipe - Histórico de Preços](https://www.kaggle.com/datasets/franckepeixoto/tabela-fipe/data).

To make this analysis we will need to ingest the data, then elaborate the dashboard.
1) Understanding the data.
2) Put the databases at work.
 - MySQL.
```bash
docker run --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root -d mysql
docker exec -it mysql /bin/bash
mysql -uroot -h127.0.0.1 -proot
create user fleet_analyst identified by 'superSecret';
grant all on fleet.* to fleet_analyst;
flush privileges;
```
 - PostgreSQL

 ```bash
docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres
docker exec -it postgres /bin/bash
psql -U postgres  
create user fleet_analyst with password 'superSecret';
create database fleet OWNER fleet_analyst;
 ```

 - MongoDB
 ```bash
docker run -d --name mongo -p 27017:27017 -e MONGO_INITDB_ROOT_USERNAME=mongoadmin -e MONGO_INITDB_ROOT_PASSWORD=secret mongo
docker exec -it mongo /bin/bash
mongosh -u mongoadmin -p secret
use fleet
```


```javascript
db.createUser({
  user: "fleet_analyst",
  pwd: "superSecret",
  roles: [
    { role: "readWrite", db: "fleet" },
    { role: "dbAdmin", db: "fleet" }
  ]
})
```

If you create the user in the admin database, then you'll need to change the login database.

```
mongodb://fleet_analyst:superSecret@127.0.0.1:27017/fleet?authSource=admin
```
All files for January and July.

MySQL
```sql
select * from fleet_month where month(month) in (1,7);
```

PostgreSQL
```sql
SELECT * FROM fleet_month WHERE EXTRACT(MONTH FROM month) IN (1, 7);
```

MongoDB
```javascript
db.fleet_month.find({ $expr: { $in: [{ $month: "$month" },[1, 7]]}})
```



3) 
2) Importing the data and sani.
3) 
3) Building the dash board.
4) Making some analysis.


## L