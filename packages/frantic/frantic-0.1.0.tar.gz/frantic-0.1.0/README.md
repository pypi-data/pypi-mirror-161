# Frantic

Firestore with Pydantic models integration.

Please note that this module is a work in progress. API may change over time. Also, the code is not tested yet
and there are no security checks run periodically.

## Basic usage

If you have your service account key path set in `GOOGLE_APPLICATION_CREDENTIALS`, it's fairly easy:

```python
import asyncio
from typing import ClassVar
from frantic import Frantic, BaseModel


# Create a model the same way you would do it with Pydantic
class User(BaseModel):
    # optionally, you may specify name of collection instances will be stored within:
    collection: ClassVar = "my_users_collection"
    # field 'id' is added automatically
    name: str


async def main():
    frantic = Frantic()

    user = User(name="ijustfarted")

    # Save user in the Firestore db
    await frantic.add(user)

    # user's id gets automatically populated and can be used to retrieve the user
    retrieved = await frantic.get(User, user.id)
    assert retrieved.name == user.name

    # list all users
    users = await frantic.list(User)

    # delete user
    await frantic.delete(user)
    # or
    await frantic.delete(User, user.id)

if __name__ == "__main__":
    asyncio.run(main)
```
