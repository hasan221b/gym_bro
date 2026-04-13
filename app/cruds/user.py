from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from app.cruds.base import CRUDBase
from app.models.users import User
from app.schemas.user import UserCreate


class UserCRUD(CRUDBase[User]):

    async def upsert(self, db: AsyncSession, data: UserCreate) -> None:
        """
        Insert the user if they don't exist, update their info if they do.
        Called every time a user interacts with the Telegram bot.
        """
        stmt = (
            insert(User)
            .values(
                id=data.id,
                username=data.username,
                first_name=data.first_name,
                last_name=data.last_name,
            )
            .on_conflict_do_update(
                index_elements=["id"],
                set_={
                    "username": data.username,
                    "first_name": data.first_name,
                    "last_name": data.last_name,
                },
            )
        )
        await db.execute(stmt)
        await db.commit()


user_crud = UserCRUD(User)
