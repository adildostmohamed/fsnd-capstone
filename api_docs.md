# Casting Agency API Definition

## Movies

### Get Movies

Get movies

#### Method

GET

#### Endpoint

`/movies`

#### URL Params

None

#### Query Params

None

#### Data params

None

#### Success response

- Status code: `200`
- Response:

```
'success': Boolean,
'total_movies': Int,
'movies': [
   {
      id: Id,
      title: String,
      release_date: Date,
      actors: {
        total_actors: Int,
        actors: [
          {
            id: Id,
            name: String,
            gender: String
          }, ...]
      }
   }, ...]
```

#### Errors

- Not authenticated
  - Status code: `401`
- Internal server error
  - Status code: `500`


### Get Movies

Create a new movie

#### Method

POST

#### Endpoint

`/movies`

#### URL Params

None

#### Query Params

None

#### Req Body Params

```
{
   title: String,
   release_date: Date,
   actors?: [Id]
}
```

#### Success response

- Status code: `201`
- Response:

```
'success': Boolean,
'movie': {
   id: Id,
   title: String,
   release_date: Date,
   actors: {
     total_actors: Int,
     actors: [
       {
         id: Id,
         name: String,
         gender: String
       }, ...]
   }
 }
```

#### Errors

- Insufficient permissions
  - Status code: `403`
- Not authenticated
  - Status code: `401`
- Internal server error
  - Status code: `500`
