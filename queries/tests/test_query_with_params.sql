@foo = #{foo};
@bar = #{bar};

select *
from flarp
where
  field1 = @foo
  and field2 = @bar
