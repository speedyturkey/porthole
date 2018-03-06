@foo = #{foo};
@bar = #{b_ar};
@baz = #{Baz};

select *
from flarp
where
  field1 = @foo
  and field2 = @bar
  and field3 = @baz