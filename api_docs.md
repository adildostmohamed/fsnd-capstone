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


### Create Movie

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

- Missing required data
  - Status code: `400`
- Invalid date format
  - Status code: `422`
- Not authenticated
  - Status code: `401`
- Insufficient permissions
  - Status code: `403`
- Internal server error
  - Status code: `500`
  
### Get a movie
Get a new movie

#### Method
GET

#### Endpoint
`/movies/:id`

#### URL Params
`movie_id`

#### Query Params
None

#### Req Body Params
None

#### Success response
- Status code: `200`
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

- Could not find movie
  - Status code: `404`
- Not authenticated
  - Status code: `401`
- Insufficient permissions
  - Status code: `403`
- Internal server error
  - Status code: `500`

### Update a movie
Update a movie by id

#### Method
PATCH

#### Endpoint
`/movies/:id`

#### URL Params
`movie_id`

#### Query Params
None

#### Req Body Params
```
{
   title?: String,
   release_date?: Date,
   actors?: [Id]
}
```

#### Success response
- Status code: `200`
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

- Could not find movie
  - Status code: `404`
- Missing required data
  - Status code: `400`
- Not authenticated
  - Status code: `401`
- Insufficient permissions
  - Status code: `403`
- Internal server error
  - Status code: `500`
  
  
### Delete a movie
Delete a movie by id

#### Method
DELETE

#### Endpoint
`/movies/:id`

#### URL Params
`movie_id`

#### Query Params
None

#### Req Body Params
None

#### Success response
- Status code: `200`
- Response:
```
'success': Boolean,
'movie_id': Id
```

#### Errors

- Could not find movie
  - Status code: `404`
- Missing required data
  - Status code: `400`
- Not authenticated
  - Status code: `401`
- Insufficient permissions
  - Status code: `403`
- Internal server error
  - Status code: `500`
